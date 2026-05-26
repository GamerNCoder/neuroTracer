#!/usr/bin/env python3
"""
Train HumanScore calibration from pre-2012 blog corpus + synthetic AI text.

Usage:
  cd arnav/neurotracer
  source venv/bin/activate
  python3 scripts/train_from_blogs.py

  # Quick test on 40 posts
  python3 scripts/train_from_blogs.py --max-human 40
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from engine.training.tune_blogs import evaluate_loaded_calibration, train_blog_calibration


def main() -> int:
    p = argparse.ArgumentParser(description="Train local human vs AI calibration")
    p.add_argument(
        "--corpus",
        type=Path,
        default=_ROOT / "data" / "human" / "blogs-pre2012",
    )
    p.add_argument(
        "--output",
        type=Path,
        default=_ROOT / "data" / "models" / "calibration.json",
    )
    p.add_argument("--max-human", type=int, default=None, help="Limit posts for quick runs")
    p.add_argument("--test-size", type=float, default=0.2)
    args = p.parse_args()

    print("Loading human corpus and building synthetic AI pairs...")
    result = train_blog_calibration(
        corpus_dir=args.corpus,
        output_path=args.output,
        test_size=args.test_size,
        max_human=args.max_human,
    )
    eval_after = evaluate_loaded_calibration(args.corpus)
    print(f"Saved: {result['_path']}")
    print(f"Human samples: {result['human_samples']}")
    print(f"AI samples:    {result['ai_samples']}")
    print(f"Threshold:     {result['threshold']}")
    print(f"Holdout:       {result['metrics']}")
    print(f"Blog corpus:   {result.get('blog_corpus_eval')}")
    print(f"AI holdout:    {result.get('ai_holdout_eval')}")
    print(f"Live eval:     {eval_after}")
    print("Marker weights (from logistic coefficients):")
    for m, w in result["marker_weights"].items():
        print(f"  {m:12} {w:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
