"""
Hedging Language Detector
Detects uncertainty markers and hedging patterns - humans use more varied hedging
"""

from typing import List, Dict, Any
import re


class HedgingDetector:
    """
    Detects hedging language patterns.
    Humans show more inconsistent and varied hedging than AI.
    """
    
    def __init__(self):
        # Comprehensive hedging word lists
        self.hedging_modals = {
            "maybe", "perhaps", "possibly", "probably", "likely", "unlikely",
            "might", "could", "may", "would", "should"
        }
        
        self.hedging_verbs = {
            "seems", "appears", "suggests", "indicates", "implies",
            "think", "believe", "assume", "presume", "suppose"
        }
        
        self.hedging_adverbs = {
            "roughly", "approximately", "about", "around", "somewhat",
            "rather", "quite", "fairly", "relatively", "generally"
        }
        
        self.hedging_phrases = [
            r"i\s+(think|believe|feel|guess|suppose)",
            r"it\s+(seems|appears|looks)\s+(like|that|as\s+if)",
            r"(kind\s+of|sort\s+of)",
            r"(more\s+or\s+less)",
            r"(to\s+some\s+extent)",
            r"(in\s+a\s+way)",
        ]
    
    def detect(self, text: str, sentences: List[str]) -> Dict[str, Any]:
        """
        Detect hedging patterns in text
        
        Args:
            text: Full cleaned text
            sentences: List of sentences
            
        Returns:
            Dictionary with hedging metrics
        """
        text_lower = text.lower()
        
        # Count hedging words
        modal_count = sum(1 for word in self.hedging_modals if word in text_lower)
        verb_count = sum(1 for word in self.hedging_verbs if word in text_lower)
        adverb_count = sum(1 for word in self.hedging_adverbs if word in text_lower)
        
        # Count hedging phrases
        phrase_count = sum(
            1 for pattern in self.hedging_phrases
            if re.search(pattern, text_lower)
        )
        
        total_hedging = modal_count + verb_count + adverb_count + phrase_count
        
        # Analyze distribution across sentences
        sentence_hedging = [self._count_sentence_hedging(s) for s in sentences]
        hedging_variance = self._calculate_variance(sentence_hedging) if len(sentence_hedging) > 1 else 0.0
        
        # Normalize by text length
        word_count = len(text.split())
        hedging_density = total_hedging / max(1, word_count / 100)  # Per 100 words
        
        # Score: higher density + higher variance = more human-like
        # Humans hedge inconsistently, AI hedges more uniformly
        density_score = min(1.0, hedging_density / 5.0)  # Normalize
        variance_score = min(1.0, hedging_variance / 2.0)  # Normalize
        
        hedging_score = (density_score * 0.5 + variance_score * 0.5)
        
        return {
            "hedging_score": float(hedging_score),
            "total_hedging": total_hedging,
            "modal_count": modal_count,
            "verb_count": verb_count,
            "adverb_count": adverb_count,
            "phrase_count": phrase_count,
            "hedging_density": float(hedging_density),
            "hedging_variance": float(hedging_variance),
            "sentence_hedging": sentence_hedging
        }
    
    def _count_sentence_hedging(self, sentence: str) -> int:
        """Count hedging markers in a single sentence"""
        sentence_lower = sentence.lower()
        count = 0
        
        # Count words
        words = set(sentence_lower.split())
        count += len(words & self.hedging_modals)
        count += len(words & self.hedging_verbs)
        count += len(words & self.hedging_adverbs)
        
        # Count phrases
        for pattern in self.hedging_phrases:
            if re.search(pattern, sentence_lower):
                count += 1
        
        return count
    
    def _calculate_variance(self, values: List[int]) -> float:
        """Calculate variance of a list"""
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
