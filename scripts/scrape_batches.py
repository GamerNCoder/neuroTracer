#!/usr/bin/env python3
"""
Scrape pre-2012 blogs in resumable batches toward a target corpus size (e.g. 1000).

Each invocation saves at most --batch-size new posts, then exits. Re-run until
--target is reached. Safe to interrupt (Ctrl+C) between batches.

Examples:
  # Toward 1000 posts, 100 per run (~10 runs, ~30–60 min each depending on network)
  python3 scripts/scrape_batches.py --target 1000 --batch-size 100

  # One batch only
  python3 scripts/scrape_batches.py --target 1000 --batch-size 100 --once

  # Then build ML-ready dataset
  python3 scripts/build_local_dataset.py
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from engine.scraper.categories import ALL_CATEGORIES, CATEGORIES
from engine.scraper.runner import ScrapeRunner
from engine.scraper.storage import CorpusWriter
from engine.scraper.wayback import WaybackClient


def main() -> int:
    p = argparse.ArgumentParser(description="Batch scrape pre-2012 blogs toward a target size")
    p.add_argument("--output", type=Path, default=_ROOT / "data" / "human" / "blogs-pre2012")
    p.add_argument("--target", type=int, default=1000, help="Total posts to collect")
    p.add_argument("--batch-size", type=int, default=100, help="Max new posts per run")
    p.add_argument("--delay", type=float, default=1.25)
    p.add_argument("--min-chars", type=int, default=200)
    p.add_argument("--extended", action="store_true", help="Use 41 CDX patterns (20+21)")
    p.add_argument("--once", action="store_true", help="Single batch then exit")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    log = logging.getLogger("scrape_batches")

    out = args.output.expanduser().resolve()
    writer = CorpusWriter(out)
    have = writer.count_ok()
    need = max(0, args.target - have)

    if need == 0:
        log.info("Corpus already at %d posts (target %d). Run build_local_dataset.py", have, args.target)
        return 0

    pool = ALL_CATEGORIES if args.extended else CATEGORIES
    per_cat = max(25, (args.target + len(pool) - 1) // len(pool))

    log.info("Corpus: %d ok | target: %d | need: %d | batch-size: %d", have, args.target, need, args.batch_size)
    log.info("Categories: %d | ~%d per category | extended=%s", len(pool), per_cat, args.extended)

    batch_cap = min(args.batch_size, need)

    with WaybackClient(request_delay_sec=args.delay) as client:
        runner = ScrapeRunner(
            writer,
            client,
            per_category=per_cat,
            max_categories=len(pool),
            min_plaintext_chars=args.min_chars,
            global_target=args.target,
            batch_limit=batch_cap,
            use_extended_categories=args.extended,
        )
        stats = runner.run()

    total = writer.count_ok()
    log.info(
        "Batch done. saved=%d this run | total=%d/%d | failed=%d skipped=%d",
        stats.items_saved,
        total,
        args.target,
        stats.items_failed,
        stats.items_skipped,
    )
    log.info("Manifest: %s | Batches log: %s", writer.manifest_path, writer.batches_path)

    if not args.once and total < args.target:
        remaining = args.target - total
        est_min = int(remaining * args.delay / 60)
        log.info("Re-run: python3 scripts/scrape_batches.py --target %d --batch-size %d", args.target, args.batch_size)
        log.info("~%d posts left (~%d+ min at %.1fs/req)", remaining, est_min, args.delay)

    return 0 if stats.items_saved > 0 or total >= args.target else 1


if __name__ == "__main__":
    raise SystemExit(main())
