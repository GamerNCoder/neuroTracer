"""
HumanScore Engine - Main scoring logic
Fuses multiple cognitive markers into a single HumanScore™
"""

from pathlib import Path
from typing import Dict, Any, Optional

from engine.humanscore.calibration import CalibrationModel, load_calibration
from engine.markers.drift.analyzer import DriftAnalyzer
from engine.markers.cadence.analyzer import CadenceAnalyzer
from engine.markers.hedging.detector import HedgingDetector
from engine.markers.metaphor.counter import MetaphorCounter
from engine.markers.coherence.analyzer import CoherenceAnalyzer
from engine.markers.stylometry.extractor import StylometricExtractor


class HumanScoreEngine:
    """
    Main scoring engine that combines cognitive markers
    into a unified HumanScore™ (0-1 scale)
    """
    
    def __init__(
        self,
        *,
        use_calibration: bool = True,
        calibration_path: Optional[Path] = None,
    ):
        self.calibration: Optional[CalibrationModel] = None
        if use_calibration:
            self.calibration = load_calibration(calibration_path)

        # Default heuristic weights; overridden when calibration is loaded
        self.weights = {
            "drift": 0.20,
            "cadence": 0.15,
            "hedging": 0.15,
            "metaphor": 0.10,
            "coherence": 0.20,
            "stylometry": 0.20,
        }
        if self.calibration and self.calibration.marker_weights:
            self.weights = dict(self.calibration.marker_weights)

        # Initialize marker analyzers
        self.drift_analyzer = DriftAnalyzer()
        self.cadence_analyzer = CadenceAnalyzer()
        self.hedging_detector = HedgingDetector()
        self.metaphor_counter = MetaphorCounter()
        self.coherence_analyzer = CoherenceAnalyzer()
        self.stylometric_extractor = StylometricExtractor()
    
    def score(self, processed_text: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate HumanScore™ from processed text
        
        Args:
            processed_text: Output from TextProcessor
            
        Returns:
            Dictionary with humanscore, breakdown, and metadata
        """
        # Extract marker scores using actual analyzers
        drift_result = self.drift_analyzer.analyze(processed_text["sentences"])
        cadence_result = self.cadence_analyzer.analyze(
            processed_text["sentences"],
            processed_text["tokens"]
        )
        hedging_result = self.hedging_detector.detect(
            processed_text["cleaned"],
            processed_text["sentences"]
        )
        metaphor_result = self.metaphor_counter.count(
            processed_text["cleaned"],
            processed_text["sentences"]
        )
        coherence_result = self.coherence_analyzer.analyze(processed_text["sentences"])
        stylometry_result = self.stylometric_extractor.extract(
            processed_text["cleaned"],
            processed_text["sentences"],
            processed_text["tokens"]
        )
        
        # Extract scores from results
        marker_scores = {
            "drift": drift_result["drift_score"],
            "cadence": cadence_result["cadence_score"],
            "hedging": hedging_result["hedging_score"],
            "metaphor": metaphor_result["metaphor_score"],
            "coherence": coherence_result["coherence_score"],
            "stylometry": stylometry_result["stylometry_score"]
        }
        
        breakdown = {
            marker: round(score, 4) for marker, score in marker_scores.items()
        }

        if self.calibration:
            prob_human = self.calibration.predict_proba_human(breakdown)
            humanscore = prob_human
            classification = self.calibration.classify(prob_human)
            confidence = self.calibration.confidence(prob_human)
        else:
            humanscore = sum(
                breakdown[m] * self.weights[m] for m in breakdown
            )
            classification = (
                "likely_human"
                if humanscore >= 0.6
                else "likely_ai"
                if humanscore <= 0.4
                else "uncertain"
            )
            confidence = round(min(1.0, abs(humanscore - 0.5) * 2), 4)

        return {
            "humanscore": round(humanscore, 4),
            "breakdown": breakdown,
            "classification": classification,
            "confidence": confidence,
            "calibrated": self.calibration is not None,
            "metadata": {
                "sentence_count": processed_text["sentence_count"],
                "token_count": processed_text["token_count"],
                "char_count": processed_text["char_count"],
                "calibration_version": (
                    self.calibration.version if self.calibration else None
                ),
                "marker_details": {
                    "drift": drift_result,
                    "cadence": cadence_result,
                    "hedging": hedging_result,
                    "metaphor": metaphor_result,
                    "coherence": coherence_result,
                    "stylometry": stylometry_result
                }
            }
        }

