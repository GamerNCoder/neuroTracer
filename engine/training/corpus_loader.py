"""Load human blog corpus from scraped pre-2012 export."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

from engine.preprocessing.html_text import extract_text_from_bytes

DEFAULT_CORPUS = Path(__file__).resolve().parents[2] / "data" / "human" / "blogs-pre2012"


def iter_human_posts(
    corpus_dir: Path | None = None,
    *,
    min_chars: int = 200,
    max_posts: int | None = None,
) -> Iterator[dict]:
    """
    Yield dicts: id, category, title, text, source_url.
    """
    root = (corpus_dir or DEFAULT_CORPUS).expanduser().resolve()
    manifest = root / "manifest.jsonl"
    if not manifest.exists():
        raise FileNotFoundError(f"Missing manifest: {manifest}")

    count = 0
    seen: set[str] = set()
    with manifest.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get("status") != "ok":
                continue
            post_id = row.get("id", "")
            if post_id in seen:
                continue
            seen.add(post_id)

            rel = row.get("html_path") or ""
            html_path = root / rel
            if not html_path.is_file():
                continue
            text = extract_text_from_bytes(html_path.read_bytes(), html_path.name)
            if len(text) < min_chars:
                continue

            yield {
                "id": post_id,
                "category": row.get("category", ""),
                "title": row.get("title"),
                "text": text,
                "source_url": row.get("source_url", ""),
            }
            count += 1
            if max_posts is not None and count >= max_posts:
                return


def load_human_texts(
    corpus_dir: Path | None = None,
    *,
    min_chars: int = 200,
    max_posts: int | None = None,
) -> list[str]:
    return [p["text"] for p in iter_human_posts(corpus_dir, min_chars=min_chars, max_posts=max_posts)]
