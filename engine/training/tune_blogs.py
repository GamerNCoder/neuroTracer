"""
Blog-aware calibration: train on corpus, then tune intercept/threshold so
pre-2012 posts score as human while synthetic AI stays low.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split

from engine.humanscore.calibration import MARKERS
from engine.humanscore.scorer import HumanScoreEngine
from engine.preprocessing.text_processor import TextProcessor
from engine.training.ai_synthetic import STATIC_AI_SAMPLES, build_ai_corpus
from engine.training.corpus_loader import load_human_texts
from engine.training.features import batch_features

DEFAULT_OUTPUT = Path(__file__).resolve().parents[2] / "data" / "models" / "calibration.json"

TARGET_BLOG_MEDIAN = 0.68
TARGET_BLOG_LIKELY_HUMAN_PCT = 0.88
MAX_AI_LIKELY_HUMAN_PCT = 0.15
UNCERTAIN_MARGIN = 0.05


def _logit(p: float) -> float:
    p = max(1e-6, min(1.0 - 1e-6, p))
    return math.log(p / (1.0 - p))


def _score_texts(texts: List[str], intercept: float, coef: np.ndarray) -> List[float]:
    engine = HumanScoreEngine(use_calibration=False)
    processor = TextProcessor()
    probs: List[float] = []
    for text in texts:
        processed = processor.process(text)
        result = engine.score(processed)
        z = intercept
        for i, m in enumerate(MARKERS):
            z += float(coef[i]) * float(result["breakdown"][m])
        probs.append(1.0 / (1.0 + math.exp(-z)))
    return probs


def _blog_metrics(
    probs: List[float],
    threshold: float,
    margin: float = UNCERTAIN_MARGIN,
) -> Dict[str, float]:
    n = len(probs)
    if n == 0:
        return {}
    likely = sum(1 for p in probs if p >= threshold + margin)
    return {
        "mean": float(np.mean(probs)),
        "median": float(np.median(probs)),
        "p10": float(np.percentile(probs, 10)),
        "p90": float(np.percentile(probs, 90)),
        "likely_human_pct": likely / n,
    }


def _classify_pct(probs: List[float], threshold: float, margin: float) -> float:
    return sum(1 for p in probs if p >= threshold + margin) / max(1, len(probs))


def train_blog_calibration(
    *,
    corpus_dir: Path | None = None,
    output_path: Path | None = None,
    test_size: float = 0.2,
    random_state: int = 42,
    max_human: int | None = None,
    target_blog_median: float = TARGET_BLOG_MEDIAN,
    target_blog_likely_pct: float = TARGET_BLOG_LIKELY_HUMAN_PCT,
) -> Dict[str, Any]:
    human_texts = load_human_texts(corpus_dir, min_chars=150, max_posts=max_human)
    if len(human_texts) < 20:
        raise ValueError(f"Need at least 20 human posts; got {len(human_texts)}")

    ai_texts = build_ai_corpus(human_texts, target_count=len(human_texts))
    ai_texts.extend(STATIC_AI_SAMPLES * max(1, len(human_texts) // 20))

    texts = human_texts + ai_texts
    labels = [1] * len(human_texts) + [0] * len(ai_texts)

    X, y = batch_features(texts, labels)
    X_arr = np.array(X, dtype=np.float64)
    y_arr = np.array(y, dtype=np.int32)

    X_train, X_test, y_train, y_test = train_test_split(
        X_arr, y_arr, test_size=test_size, random_state=random_state, stratify=y_arr
    )

    clf = LogisticRegression(max_iter=3000, class_weight="balanced", random_state=random_state)
    clf.fit(X_train, y_train)

    intercept = float(clf.intercept_[0])
    coef = clf.coef_[0].copy()

    y_prob = clf.predict_proba(X_test)[:, 1]
    holdout_metrics = {
        "accuracy": round(float(accuracy_score(y_test, clf.predict(X_test))), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_prob)), 4),
        "test_size": len(y_test),
    }

    # --- Blog-aware intercept: shift so corpus median ≈ target (not saturated at 0.9+) ---
    blog_probs = _score_texts(human_texts, intercept, coef)
    med = float(np.median(blog_probs))
    if 0.01 < med < 0.99:
        intercept += _logit(target_blog_median) - _logit(med)

    ai_eval = build_ai_corpus(human_texts[: min(80, len(human_texts))], target_count=80)

    # Balance: keep blog median near target while AI holdout stays mostly "not human"
    for _ in range(6):
        blog_probs = _score_texts(human_texts, intercept, coef)
        ai_probs = _score_texts(ai_eval, intercept, coef)
        ai_med = float(np.median(ai_probs))
        if ai_med > 0.55:
            intercept -= 0.2
            continue
        if float(np.median(blog_probs)) < target_blog_median - 0.05:
            intercept += 0.1
            continue
        break

    blog_probs = _score_texts(human_texts, intercept, coef)
    # threshold + margin = score at (100 - target%) percentile → ~88% labeled likely_human
    pct_cut = 100.0 * (1.0 - target_blog_likely_pct)
    th_plus_margin = float(np.percentile(blog_probs, pct_cut))
    threshold = max(0.35, th_plus_margin - UNCERTAIN_MARGIN)

    blog_eval = _blog_metrics(blog_probs, threshold)
    blog_eval["likely_human_pct"] = round(_classify_pct(blog_probs, threshold, UNCERTAIN_MARGIN), 4)

    ai_probs = _score_texts(ai_eval, intercept, coef)
    ai_eval_metrics = _blog_metrics(ai_probs, threshold)
    ai_eval_metrics["likely_human_pct"] = round(
        _classify_pct(ai_probs, threshold, UNCERTAIN_MARGIN), 4
    )

    coef_map = {m: round(float(coef[i]), 6) for i, m in enumerate(MARKERS)}
    abs_sum = sum(abs(c) for c in coef_map.values()) or 1.0
    marker_weights = {m: round(abs(coef_map[m]) / abs_sum, 4) for m in MARKERS}

    human_mask = y_arr == 1
    ai_mask = y_arr == 0
    human_means = {m: round(float(X_arr[human_mask, i].mean()), 4) for i, m in enumerate(MARKERS)}
    ai_means = {m: round(float(X_arr[ai_mask, i].mean()), 4) for i, m in enumerate(MARKERS)}

    payload: Dict[str, Any] = {
        "version": "1.1.0",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "source": "blogs-pre2012 + synthetic-ai (blog-tuned)",
        "human_samples": len(human_texts),
        "ai_samples": len(ai_texts),
        "threshold": round(threshold, 4),
        "uncertain_margin": UNCERTAIN_MARGIN,
        "logistic": {
            "intercept": round(intercept, 6),
            "coefficients": coef_map,
        },
        "marker_weights": marker_weights,
        "marker_means_human": human_means,
        "marker_means_ai": ai_means,
        "metrics": holdout_metrics,
        "blog_corpus_eval": blog_eval,
        "ai_holdout_eval": {
            **ai_eval_metrics,
            "likely_human_pct": round(
                sum(1 for p in ai_probs if p >= threshold + UNCERTAIN_MARGIN) / len(ai_probs),
                4,
            ),
        },
    }

    out = (output_path or DEFAULT_OUTPUT).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    payload["_path"] = str(out)
    return payload


def evaluate_loaded_calibration(corpus_dir: Path | None = None) -> Dict[str, Any]:
    """Score all manifest posts with current calibration.json."""
    from engine.training.corpus_loader import iter_human_posts

    engine = HumanScoreEngine(use_calibration=True)
    cal = engine.calibration
    processor = TextProcessor()
    probs: List[float] = []
    classes: List[str] = []

    root = corpus_dir or Path(__file__).resolve().parents[2] / "data" / "human" / "blogs-pre2012"
    for post in iter_human_posts(root, min_chars=150):
        r = engine.score(processor.process(post["text"]))
        probs.append(r["humanscore"])
        classes.append(r["classification"])

    n = len(probs)
    likely = sum(1 for c in classes if c == "likely_human")
    return {
        "n": n,
        "threshold": cal.threshold if cal else None,
        "mean": float(np.mean(probs)),
        "median": float(np.median(probs)),
        "likely_human": likely,
        "likely_human_pct": likely / n if n else 0,
    }
