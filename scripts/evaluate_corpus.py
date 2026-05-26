#!/usr/bin/env python3
"""Score all human blog posts and print distribution metrics."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from engine.humanscore.scorer import HumanScoreEngine
from engine.preprocessing.html_text import extract_text_from_bytes
from engine.training.corpus_loader import iter_human_posts


def main() -> int:
    corpus = _ROOT / "data" / "human" / "blogs-pre2012"
    engine = HumanScoreEngine(use_calibration=True)
    scores: list[float] = []
    by_cat: dict[str, list[float]] = {}
    misclassified: list[dict] = []

    for post in iter_human_posts(corpus, min_chars=150):
        text = post["text"]
        from engine.preprocessing.text_processor import TextProcessor

        r = engine.score(TextProcessor().process(text))
        s = r["humanscore"]
        scores.append(s)
        cat = post["category"]
        by_cat.setdefault(cat, []).append(s)
        if r["classification"] != "likely_human":
            misclassified.append(
                {
                    "id": post["id"],
                    "category": cat,
                    "humanscore": s,
                    "classification": r["classification"],
                    "breakdown": r["breakdown"],
                    "chars": len(text),
                }
            )

    n = len(scores)
    if n == 0:
        print("No posts scored")
        return 1

    scores_sorted = sorted(scores)
    mean = sum(scores) / n
    median = scores_sorted[n // 2]
    p10 = scores_sorted[max(0, n // 10 - 1)]
    p90 = scores_sorted[min(n - 1, (9 * n) // 10)]
    cal = engine.calibration
    th = cal.threshold if cal else 0.5
    margin = cal.uncertain_margin if cal else 0.08
    from engine.training.corpus_loader import iter_human_posts as _iter
    from engine.preprocessing.text_processor import TextProcessor

    class_counts: dict[str, int] = {}
    for post in _iter(corpus, min_chars=150):
        r = engine.score(TextProcessor().process(post["text"]))
        class_counts[r["classification"]] = class_counts.get(r["classification"], 0) + 1

    print(f"Posts: {n}")
    print(f"Calibration threshold: {th}  margin: {margin}")
    print(f"Mean: {mean:.4f}  Median: {median:.4f}  P10: {p10:.4f}  P90: {p90:.4f}")
    print(f"By classification: {class_counts}")
    print(f"likely_human (API label): {class_counts.get('likely_human', 0)}/{n} ({100*class_counts.get('likely_human',0)/n:.1f}%)")
    print("\nPer category (mean score):")
    for cat in sorted(by_cat):
        xs = by_cat[cat]
        print(f"  {cat:16} n={len(xs):3} mean={sum(xs)/len(xs):.3f}")

    out = corpus / "eval_report.json"
    out.write_text(
        json.dumps(
            {
                "n": n,
                "threshold": th,
                "mean": mean,
                "median": median,
                "likely_human_pct": class_counts.get("likely_human", 0) / n,
                "misclassified": misclassified[:30],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
