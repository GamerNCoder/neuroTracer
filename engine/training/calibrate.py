"""Train logistic calibration on marker features."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split

from engine.training.ai_synthetic import build_ai_corpus
from engine.training.corpus_loader import load_human_texts
from engine.training.features import MARKERS, batch_features

DEFAULT_OUTPUT = Path(__file__).resolve().parents[2] / "data" / "models" / "calibration.json"


def train_calibration(
    *,
    corpus_dir: Path | None = None,
    output_path: Path | None = None,
    test_size: float = 0.2,
    random_state: int = 42,
    max_human: int | None = None,
) -> Dict[str, Any]:
    human_texts = load_human_texts(corpus_dir, min_chars=200, max_posts=max_human)
    if len(human_texts) < 20:
        raise ValueError(f"Need at least 20 human posts; got {len(human_texts)}")

    ai_texts = build_ai_corpus(human_texts, target_count=len(human_texts))
    texts = human_texts + ai_texts
    labels = [1] * len(human_texts) + [0] * len(ai_texts)

    X, y = batch_features(texts, labels)
    X_arr = np.array(X, dtype=np.float64)
    y_arr = np.array(y, dtype=np.int32)

    X_train, X_test, y_train, y_test = train_test_split(
        X_arr, y_arr, test_size=test_size, random_state=random_state, stratify=y_arr
    )

    clf = LogisticRegression(max_iter=2000, random_state=random_state)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]
    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "f1_human": round(float(f1_score(y_test, y_pred, pos_label=1)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_prob)), 4),
        "test_size": len(y_test),
        "train_size": len(y_train),
    }

    # Optimal threshold on train set (Youden-style: maximize accuracy)
    train_prob = clf.predict_proba(X_train)[:, 1]
    best_t, best_acc = 0.5, 0.0
    for t in np.linspace(0.35, 0.65, 31):
        pred = (train_prob >= t).astype(int)
        acc = accuracy_score(y_train, pred)
        if acc > best_acc:
            best_acc = acc
            best_t = float(t)

    coef = clf.coef_[0]
    coef_map = {m: round(float(coef[i]), 6) for i, m in enumerate(MARKERS)}
    # Positive coef → more human; normalize to weights for display
    abs_sum = sum(abs(c) for c in coef_map.values()) or 1.0
    marker_weights = {m: round(abs(coef_map[m]) / abs_sum, 4) for m in MARKERS}

    human_means, ai_means = _class_means(X_arr, y_arr)

    payload: Dict[str, Any] = {
        "version": "1.0.0",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "source": "blogs-pre2012 + synthetic-ai",
        "human_samples": len(human_texts),
        "ai_samples": len(ai_texts),
        "threshold": round(best_t, 4),
        "logistic": {
            "intercept": round(float(clf.intercept_[0]), 6),
            "coefficients": coef_map,
        },
        "marker_weights": marker_weights,
        "marker_means_human": human_means,
        "marker_means_ai": ai_means,
        "metrics": metrics,
    }

    out = (output_path or DEFAULT_OUTPUT).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    payload["_path"] = str(out)
    return payload


def _class_means(X: np.ndarray, y: np.ndarray) -> Tuple[Dict[str, float], Dict[str, float]]:
    human = X[y == 1]
    ai = X[y == 0]
    h_mean = human.mean(axis=0) if len(human) else np.zeros(len(MARKERS))
    a_mean = ai.mean(axis=0) if len(ai) else np.zeros(len(MARKERS))
    return (
        {m: round(float(h_mean[i]), 4) for i, m in enumerate(MARKERS)},
        {m: round(float(a_mean[i]), 4) for i, m in enumerate(MARKERS)},
    )
