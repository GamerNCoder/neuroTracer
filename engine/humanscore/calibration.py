"""Load and apply blog-trained calibration for human vs AI classification."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Dict, Optional

DEFAULT_CALIBRATION_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "models" / "calibration.json"
)

MARKERS = ("drift", "cadence", "hedging", "metaphor", "coherence", "stylometry")


def _sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


class CalibrationModel:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.version = data.get("version", "1.0.0")
        self.trained_at = data.get("trained_at", "")
        self.threshold = float(data.get("threshold", 0.5))
        self.uncertain_margin = float(data.get("uncertain_margin", 0.08))
        self.intercept = float(data["logistic"]["intercept"])
        self.coefficients = {
            m: float(data["logistic"]["coefficients"][m]) for m in MARKERS
        }
        self.marker_weights = data.get("marker_weights", {})
        self.metrics = data.get("metrics", {})
        self.blog_corpus_eval = data.get("blog_corpus_eval", {})
        self.human_count = int(data.get("human_samples", 0))
        self.ai_count = int(data.get("ai_samples", 0))

    def predict_proba_human(self, breakdown: Dict[str, float]) -> float:
        z = self.intercept
        for m in MARKERS:
            z += self.coefficients[m] * float(breakdown.get(m, 0.0))
        return _sigmoid(z)

    def classify(self, prob_human: float) -> str:
        m = self.uncertain_margin
        if prob_human >= self.threshold + m:
            return "likely_human"
        if prob_human <= self.threshold - m:
            return "likely_ai"
        return "uncertain"

    def confidence(self, prob_human: float) -> float:
        """Distance from decision threshold, scaled 0–1."""
        return round(min(1.0, abs(prob_human - self.threshold) / 0.5), 4)


def load_calibration(path: Path | None = None) -> Optional[CalibrationModel]:
    p = (path or DEFAULT_CALIBRATION_PATH).expanduser().resolve()
    if not p.is_file():
        return None
    with p.open(encoding="utf-8") as f:
        data = json.load(f)
    return CalibrationModel(data)
