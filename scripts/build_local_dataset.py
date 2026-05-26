#!/usr/bin/env python3
"""
Build a local ML dataset from scraped blog HTML + manifest.jsonl.

Output under data/human/blogs-pre2012/dataset/:
  - dataset.jsonl   — one row per post (text, metadata, label=human)
  - text/{id}.txt   — plain text per post
  - stats.json      — counts, categories, char/word stats
  - splits.json     — train/val/test id lists (90/5/5 by default)
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from engine.preprocessing.html_text import extract_text_from_bytes
from engine.training.corpus_loader import iter_human_posts


def main() -> int:
    p = argparse.ArgumentParser(description="Build local dataset from blog scrape")
    p.add_argument(
        "--corpus",
        type=Path,
        default=_ROOT / "data" / "human" / "blogs-pre2012",
    )
    p.add_argument("--min-chars", type=int, default=200)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--train", type=float, default=0.9)
    p.add_argument("--val", type=float, default=0.05)
    args = p.parse_args()

    corpus = args.corpus.expanduser().resolve()
    out = corpus / "dataset"
    text_dir = out / "text"
    text_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    by_cat: dict[str, int] = {}

    for post in iter_human_posts(corpus, min_chars=args.min_chars):
        pid = post["id"]
        html_path = corpus / post.get("html_path", "")
        if html_path.is_file():
            text = extract_text_from_bytes(html_path.read_bytes(), html_path.name)
        else:
            text = post["text"]

        text_file = f"text/{pid}.txt"
        (out / text_file).write_text(text, encoding="utf-8")

        cat = post["category"]
        by_cat[cat] = by_cat.get(cat, 0) + 1
        rows.append(
            {
                "id": pid,
                "label": "human",
                "source": "blogs-pre2012",
                "category": cat,
                "title": post.get("title"),
                "source_url": post.get("source_url"),
                "char_count": len(text),
                "word_count": len(text.split()),
                "text_path": text_file,
                "text": text,
            }
        )

    if not rows:
        print("No posts found — run scrape_batches.py first", file=sys.stderr)
        return 1

    random.seed(args.seed)
    ids = [r["id"] for r in rows]
    random.shuffle(ids)
    n = len(ids)
    n_train = int(n * args.train)
    n_val = int(n * args.val)
    splits = {
        "train": ids[:n_train],
        "val": ids[n_train : n_train + n_val],
        "test": ids[n_train + n_val :],
        "seed": args.seed,
        "ratios": {"train": args.train, "val": args.val, "test": 1 - args.train - args.val},
    }

    dataset_path = out / "dataset.jsonl"
    with dataset_path.open("w", encoding="utf-8") as f:
        for row in rows:
            # Omit inline text duplicate in jsonl if huge — keep for training convenience
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    stats = {
        "built_at": datetime.now(timezone.utc).isoformat(),
        "total_posts": n,
        "by_category": by_cat,
        "total_chars": sum(r["char_count"] for r in rows),
        "mean_chars": sum(r["char_count"] for r in rows) / n,
        "mean_words": sum(r["word_count"] for r in rows) / n,
        "splits": {k: len(v) for k, v in splits.items() if k in ("train", "val", "test")},
    }
    (out / "stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    (out / "splits.json").write_text(json.dumps(splits, indent=2), encoding="utf-8")

    print(f"Dataset: {dataset_path}")
    print(f"Plain text: {text_dir} ({n} files)")
    print(f"Stats: {out / 'stats.json'}")
    print(f"Splits: train={len(splits['train'])} val={len(splits['val'])} test={len(splits['test'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
