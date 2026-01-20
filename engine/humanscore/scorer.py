"""
HumanScore Engine - Main scoring logic
Fuses multiple cognitive markers into a single HumanScore™
"""

from typing import Dict, Any
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
    
    def __init__(self):
        # Marker weights (will be tuned based on validation)
        self.weights = {
            "drift": 0.20,
            "cadence": 0.15,
            "hedging": 0.15,
            "metaphor": 0.10,
            "coherence": 0.20,
            "stylometry": 0.20
        }
        
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
        
        # Weighted fusion
        humanscore = sum(
            marker_scores[marker] * self.weights[marker]
            for marker in marker_scores
        )
        
        return {
            "humanscore": round(humanscore, 4),
            "breakdown": {
                marker: round(score, 4)
                for marker, score in marker_scores.items()
            },
            "metadata": {
                "sentence_count": processed_text["sentence_count"],
                "token_count": processed_text["token_count"],
                "char_count": processed_text["char_count"],
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

