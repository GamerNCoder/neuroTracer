#!/usr/bin/env python3
"""
Re-fetch HTML for manifest rows that have status=ok but missing .html files.

Usage:
  python3 scripts/repair_scrape_html.py
  python3 scripts/repair_scrape_html.py --corpus data/human/blogs-pre2012 --limit 10
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from engine.scraper.wayback import WaybackClient


def main() -> int:
    p = argparse.ArgumentParser(description="Re-download missing scraped HTML files")
    p.add_argument(
        "--corpus",
        type=Path,
        default=_ROOT / "data" / "human" / "blogs-pre2012",
    )
    p.add_argument("--limit", type=int, default=0, help="Max files to repair (0=all)")
    p.add_argument("--delay", type=float, default=1.25)
    args = p.parse_args()

    corpus = args.corpus.expanduser().resolve()
    manifest = corpus / "manifest.jsonl"
    if not manifest.exists():
        print(f"No manifest at {manifest}", file=sys.stderr)
        return 1

    missing: list[dict] = []
    seen_ids: set[str] = set()
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("status") != "ok":
            continue
        rid = row.get("id", "")
        if rid in seen_ids:
            continue
        seen_ids.add(rid)
        rel = row.get("html_path") or ""
        if not rel:
            continue
        path = corpus / rel
        if not path.is_file():
            missing.append(row)

    if args.limit > 0:
        missing = missing[: args.limit]

    print(f"Missing HTML files: {len(missing)}")
    if not missing:
        return 0

    repaired = 0
    failed = 0
    with WaybackClient(request_delay_sec=args.delay) as client:
        for row in missing:
            archive_url = row.get("archive_url", "")
            rel = row["html_path"]
            out = corpus / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            try:
                r = client._client.get(archive_url)
                r.raise_for_status()
                out.write_bytes(r.content)
                repaired += 1
                print(f"OK  {rel}")
            except Exception as e:
                failed += 1
                print(f"FAIL {rel}: {e}", file=sys.stderr)

    print(f"Repaired {repaired}, failed {failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
