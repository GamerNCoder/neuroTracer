"""
Batch scoring: multi-file upload and optional local filesystem paths (dev only).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from api.database import get_db
from api.routes.history import save_scoring_history
from api.utils.logger import get_logger
from engine.preprocessing.html_text import extract_text_from_bytes
from engine.preprocessing.text_processor import TextProcessor
from engine.humanscore.scorer import HumanScoreEngine

router = APIRouter()

MAX_BATCH_FILES = 64
MAX_CHARS_PER_DOC = 500_000


class BatchPathItemResult(BaseModel):
    path: str
    ok: bool
    error: Optional[str] = None
    humanscore: Optional[float] = None
    breakdown: Optional[Dict[str, float]] = None
    metadata: Optional[Dict[str, Any]] = None


class BatchPathResponse(BaseModel):
    results: List[BatchPathItemResult]
    local_path_batch_enabled: bool = True


class BatchPathsRequest(BaseModel):
    paths: List[str] = Field(default_factory=list, description="Absolute file paths")
    directory: Optional[str] = Field(
        default=None,
        description="If set, all matching files under this directory are scored",
    )
    glob_pattern: str = Field(default="*", description="Glob relative to directory, e.g. *.html")
    skip_history: bool = Field(default=True, description="Do not write each item to SQL history")


def _local_paths_allowed() -> bool:
    return os.environ.get("NEUROTRACER_ALLOW_LOCAL_PATHS", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def _path_root() -> Optional[Path]:
    raw = os.environ.get("NEUROTRACER_LOCAL_PATH_ROOT", "").strip()
    if not raw:
        return None
    return Path(raw).expanduser().resolve()


def _is_under_root(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root)
        return True
    except ValueError:
        return False


def _score_text(text: str) -> Dict[str, Any]:
    processor = TextProcessor()
    processed = processor.process(text)
    scorer = HumanScoreEngine()
    return scorer.score(processed)


def _persist(
    text: str,
    result: Dict[str, Any],
    db: Session,
    skip_history: bool,
) -> None:
    if skip_history:
        return
    save_scoring_history(
        text=text,
        humanscore=result["humanscore"],
        breakdown=result["breakdown"],
        metadata=result["metadata"],
        db=db,
    )


@router.get("/config")
async def public_config():
    """Feature flags for clients (e.g. show local path batch UI)."""
    root = os.environ.get("NEUROTRACER_LOCAL_PATH_ROOT", "").strip()
    return {
        "local_path_batch_enabled": _local_paths_allowed() and bool(root),
        "local_path_root_configured": bool(root),
    }


@router.post("/score/batch/files", response_model=BatchPathResponse)
async def score_batch_files(
    files: List[UploadFile] = File(...),
    skip_history: bool = Form(default=True),
    db: Session = Depends(get_db),
):
    """
    Score multiple uploaded files (.txt, .md, .html). Safe for production use.
    """
    logger = get_logger()
    if len(files) > MAX_BATCH_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files (max {MAX_BATCH_FILES})",
        )

    results: List[BatchPathItemResult] = []
    for uf in files:
        name = uf.filename or "upload"
        try:
            data = await uf.read()
            if len(data) > MAX_CHARS_PER_DOC * 4:
                raise ValueError("file too large")
            text = extract_text_from_bytes(data, name)
            if len(text) < 10:
                raise ValueError("extracted text too short (min 10 chars)")
            out = _score_text(text)
            _persist(text, out, db, skip_history)
            results.append(
                BatchPathItemResult(
                    path=name,
                    ok=True,
                    humanscore=out["humanscore"],
                    breakdown=out["breakdown"],
                    metadata=out["metadata"],
                )
            )
        except Exception as e:
            results.append(
                BatchPathItemResult(path=name, ok=False, error=str(e))
            )
        logger.log_scoring_request(
            text=f"[batch-file:{name}]",
            result={"batch_item": results[-1].model_dump()},
            request_options={"skip_history": skip_history},
            error=None if results[-1].ok else results[-1].error,
        )

    return BatchPathResponse(results=results, local_path_batch_enabled=False)


@router.post("/score/batch/paths", response_model=BatchPathResponse)
async def score_batch_paths(
    body: BatchPathsRequest,
    db: Session = Depends(get_db),
):
    """
    Score files from absolute paths on the API host. Disabled unless
    NEUROTRACER_ALLOW_LOCAL_PATHS=1 and NEUROTRACER_LOCAL_PATH_ROOT is set;
    every path must resolve under that root (e.g. your 2012 blog export folder).
    """
    logger = get_logger()
    if not _local_paths_allowed():
        raise HTTPException(
            status_code=403,
            detail="Local path batch disabled. Set NEUROTRACER_ALLOW_LOCAL_PATHS=1 and NEUROTRACER_LOCAL_PATH_ROOT.",
        )
    root = _path_root()
    if root is None or not root.is_dir():
        raise HTTPException(
            status_code=403,
            detail="NEUROTRACER_LOCAL_PATH_ROOT must be set to an existing directory.",
        )

    paths: List[Path] = []
    for p in body.paths:
        if p.strip():
            paths.append(Path(p).expanduser())

    if body.directory:
        d = Path(body.directory).expanduser().resolve()
        if not _is_under_root(d, root):
            raise HTTPException(status_code=400, detail="directory not under allowed root")
        if not d.is_dir():
            raise HTTPException(status_code=400, detail="directory does not exist")
        pattern = body.glob_pattern or "*"
        for f in sorted(d.glob(pattern)):
            if f.is_file() and f.suffix.lower() in (".txt", ".md", ".html", ".htm"):
                paths.append(f)

    seen = set()
    uniq: List[Path] = []
    for p in paths:
        rp = p.resolve()
        if rp in seen:
            continue
        seen.add(rp)
        uniq.append(p)

    if len(uniq) > MAX_BATCH_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"Too many paths (max {MAX_BATCH_FILES})",
        )

    results: List[BatchPathItemResult] = []
    for path in uniq:
        sp = str(path)
        try:
            rp = path.resolve()
            if not _is_under_root(rp, root):
                raise ValueError("path not under NEUROTRACER_LOCAL_PATH_ROOT")
            if not rp.is_file():
                raise ValueError("not a file")
            data = rp.read_bytes()
            if len(data) > MAX_CHARS_PER_DOC * 4:
                raise ValueError("file too large")
            text = extract_text_from_bytes(data, rp.name)
            if len(text) < 10:
                raise ValueError("extracted text too short (min 10 chars)")
            out = _score_text(text)
            _persist(text, out, db, body.skip_history)
            results.append(
                BatchPathItemResult(
                    path=sp,
                    ok=True,
                    humanscore=out["humanscore"],
                    breakdown=out["breakdown"],
                    metadata=out["metadata"],
                )
            )
        except Exception as e:
            results.append(BatchPathItemResult(path=sp, ok=False, error=str(e)))
        logger.log_scoring_request(
            text=f"[batch-path:{sp}]",
            result={"batch_item": results[-1].model_dump()},
            request_options={"skip_history": body.skip_history},
            error=None if results[-1].ok else results[-1].error,
        )

    return BatchPathResponse(results=results, local_path_batch_enabled=True)
