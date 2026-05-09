#!/usr/bin/env python3
"""
Score all .html/.htm/.txt/.md files under a directory via the TraceNeuro HTTP API.

Usage:
  export NEUROTRACER_ALLOW_LOCAL_PATHS=1
  export NEUROTRACER_LOCAL_PATH_ROOT=/path/to/parent
  ./scripts/batch_score_path.py /path/to/parent/old-blogs

Or call the API from another machine after enabling path batch on the server.

  python scripts/batch_score_path.py /data/blogs --api http://localhost:8000
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

try:
    import httpx
except ImportError:
    print("Install httpx: pip install httpx", file=sys.stderr)
    raise


def collect_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for ext in (".html", ".htm", ".txt", ".md"):
        out.extend(sorted(root.rglob(f"*{ext}")))
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Batch-score blog files via TraceNeuro API")
    p.add_argument("directory", type=Path, help="Folder of exported blog posts")
    p.add_argument(
        "--api",
        default=os.environ.get("TRACE_NEURO_API", "http://127.0.0.1:8000"),
        help="API base URL",
    )
    p.add_argument("--limit", type=int, default=64, help="Max files to send")
    args = p.parse_args()

    root = args.directory.expanduser().resolve()
    if not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        return 1

    files = collect_files(root)[: args.limit]
    if not files:
        print("No .html/.htm/.txt/.md files found.", file=sys.stderr)
        return 1

    # Prefer server-side path batch (single request) when env matches server config.
    use_paths = os.environ.get("NEUROTRACER_ALLOW_LOCAL_PATHS", "").lower() in (
        "1",
        "true",
        "yes",
    )
    path_root = os.environ.get("NEUROTRACER_LOCAL_PATH_ROOT", "").strip()

    base = args.api.rstrip("/")
    with httpx.Client(timeout=120.0) as client:
        if use_paths and path_root:
            r = client.post(
                f"{base}/api/v1/score/batch/paths",
                json={
                    "paths": [str(f) for f in files],
                    "skip_history": True,
                },
            )
        else:
            # Multipart upload fallback (works without server filesystem access).
            mp = []
            for f in files:
                mp.append(
                    ("files", (f.name, f.read_bytes(), "application/octet-stream"))
                )
            r = client.post(
                f"{base}/api/v1/score/batch/files",
                data={"skip_history": "true"},
                files=mp,
            )

    if r.status_code != 200:
        print(r.text, file=sys.stderr)
        return 1

    data = r.json()
    print(json.dumps(data, indent=2))
    failed = [x for x in data.get("results", []) if not x.get("ok")]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
