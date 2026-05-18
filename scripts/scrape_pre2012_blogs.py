#!/usr/bin/env python3
"""
Scrape pre-2012 blog posts from Internet Archive (Wayback Machine).

Default: 20 categories × 25 posts = 500 documents under data/human/blogs-pre2012/

Each item saves:
  - {category}/{id}.html — raw archived HTML
  - manifest.jsonl — one JSON line per item (timestamps, URLs, counts, title)

Usage:
  cd arnav/neurotracer
  python3 scripts/scrape_pre2012_blogs.py

  # Quick test (2 categories, 3 posts each)
  python3 scripts/scrape_pre2012_blogs.py --categories 2 --per-category 3

  # Resume after interrupt (skips URLs already in manifest.jsonl)
  python3 scripts/scrape_pre2012_blogs.py --resume

Requires network access to web.archive.org. Be polite: default 1.25s delay between requests.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# Repo root on sys.path when run as script
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from engine.scraper.runner import ScrapeRunner
from engine.scraper.storage import CorpusWriter
from engine.scraper.wayback import WaybackClient


def _default_output() -> Path:
    return _ROOT / "data" / "human" / "blogs-pre2012"


def main() -> int:
    p = argparse.ArgumentParser(
        description="Scrape pre-2012 blogs (20 categories × 25 items) via Wayback Machine"
    )
    p.add_argument(
        "--output",
        type=Path,
        default=_default_output(),
        help="Output directory (default: data/human/blogs-pre2012)",
    )
    p.add_argument(
        "--categories",
        type=int,
        default=20,
        help="Number of categories to scrape (max 20)",
    )
    p.add_argument(
        "--per-category",
        type=int,
        default=25,
        help="Posts to save per category (default 25)",
    )
    p.add_argument(
        "--delay",
        type=float,
        default=1.25,
        help="Seconds between Wayback API requests",
    )
    p.add_argument(
        "--min-chars",
        type=int,
        default=200,
        help="Minimum extracted plain-text length to keep a post",
    )
    p.add_argument(
        "--to-date",
        default="20111231",
        help="Wayback CDX 'to' date (YYYYMMDD), default end of 2011",
    )
    p.add_argument(
        "--resume",
        action="store_true",
        help="Skip URLs already recorded in manifest.jsonl (always on if manifest exists)",
    )
    p.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Debug logging",
    )
    args = p.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    log = logging.getLogger("scrape_pre2012")

    out = args.output.expanduser().resolve()
    writer = CorpusWriter(out)
    if args.resume and writer.manifest_path.exists():
        log.info("Resume mode: %d URLs already in manifest", len(writer._seen_keys))

    log.info(
        "Starting scrape → %s (%d categories × %d items)",
        out,
        min(args.categories, 20),
        args.per_category,
    )

    with WaybackClient(request_delay_sec=args.delay) as client:
        runner = ScrapeRunner(
            writer,
            client,
            per_category=args.per_category,
            max_categories=min(args.categories, 20),
            min_plaintext_chars=args.min_chars,
            to_date=args.to_date,
        )

        def on_cat(cat, idx):
            log.info("[%d/%d] Category: %s (%s)", idx + 1, args.categories, cat.name, cat.slug)

        def on_item(cat, n, total):
            log.info("  %s: %d/%d saved (files under %s/%s/)", cat.slug, n, total, out, cat.slug)

        stats = runner.run(on_category_start=on_cat, on_item_saved=on_item)

    log.info(
        "Done. saved=%d skipped=%d failed=%d categories_done=%d/%d",
        stats.items_saved,
        stats.items_skipped,
        stats.items_failed,
        stats.categories_completed,
        stats.categories_total,
    )
    log.info("Manifest: %s", writer.manifest_path)
    log.info("Summary: %s", out / "scrape_summary.json")
    return 0 if stats.items_saved > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
