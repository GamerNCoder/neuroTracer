"""Extract marker feature vectors for training."""

from __future__ import annotations

from typing import Any, Dict, List

from engine.humanscore.scorer import HumanScoreEngine
from engine.preprocessing.text_processor import TextProcessor

MARKERS = ("drift", "cadence", "hedging", "metaphor", "coherence", "stylometry")


def extract_marker_vector(text: str, engine: HumanScoreEngine | None = None) -> Dict[str, float]:
    processor = TextProcessor()
    scorer = engine or HumanScoreEngine()
    processed = processor.process(text)
    result = scorer.score(processed)
    return {m: float(result["breakdown"][m]) for m in MARKERS}


def batch_features(
    texts: List[str],
    labels: List[int],
    *,
    engine: HumanScoreEngine | None = None,
) -> tuple[List[List[float]], List[int]]:
    """
    labels: 1 = human, 0 = AI
    Returns X rows in MARKERS order, y labels.
    """
    scorer = engine or HumanScoreEngine(use_calibration=False)
    X: List[List[float]] = []
    y: List[int] = []
    for text, label in zip(texts, labels):
        vec = extract_marker_vector(text, scorer)
        X.append([vec[m] for m in MARKERS])
        y.append(label)
    return X, y
