"""Training and calibration tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engine.humanscore.calibration import load_calibration
from engine.humanscore.scorer import HumanScoreEngine
from engine.training.ai_synthetic import stylize_as_ai
from engine.training.tune_blogs import train_blog_calibration


def test_stylize_as_ai_differs():
    human = (
        "I've been thinking about this maybe we should try again. "
        "It seems odd but I don't know. Short posts aren't great though we need length."
    )
    ai = stylize_as_ai(human, seed=1)
    assert len(ai) > 50
    assert "I am" in ai or "do not" in ai or "Furthermore" in ai


def test_train_calibration_small(tmp_path):
    corpus = Path(__file__).resolve().parents[1] / "data" / "human" / "blogs-pre2012"
    if not (corpus / "manifest.jsonl").exists():
        pytest.skip("blog corpus not present locally")
    out = tmp_path / "calibration.json"
    result = train_blog_calibration(corpus_dir=corpus, output_path=out, max_human=30)
    assert out.is_file()
    assert result["human_samples"] >= 20
    assert result["metrics"]["accuracy"] >= 0.5
    data = json.loads(out.read_text())
    assert "logistic" in data


def test_scorer_uses_calibration_when_present(tmp_path):
    corpus = Path(__file__).resolve().parents[1] / "data" / "human" / "blogs-pre2012"
    if not (corpus / "manifest.jsonl").exists():
        pytest.skip("blog corpus not present locally")
    cal_path = tmp_path / "cal.json"
    train_blog_calibration(corpus_dir=corpus, output_path=cal_path, max_human=25)
    engine = HumanScoreEngine(use_calibration=True, calibration_path=cal_path)
    text = (
        "I've been wondering about this for a while. Maybe the answer isn't simple. "
        "Sometimes I change my mind mid sentence — wait, actually, let me explain differently."
    )
    from engine.preprocessing.text_processor import TextProcessor

    out = engine.score(TextProcessor().process(text))
    assert "classification" in out
    assert out["calibrated"] is True
    assert out["classification"] in ("likely_human", "likely_ai", "uncertain")
