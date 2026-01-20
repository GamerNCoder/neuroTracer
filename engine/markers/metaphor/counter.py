"""
Metaphor Rarity Counter
Detects metaphors and measures their uniqueness/rarity
Humans produce more unique metaphors than AI
"""

from typing import List, Dict, Any
import re


class MetaphorCounter:
    """
    Detects and analyzes metaphor patterns.
    Humans produce more unique and varied metaphors than AI.
    """
    
    def __init__(self):
        # Common metaphorical patterns
        self.metaphor_patterns = [
            r"\b(is|are|was|were|be|being|been)\s+\w+\s+(like|as)\s+\w+",  # "is like"
            r"\b\w+\s+(is|are|was|were)\s+\w+",  # "X is Y" (potential metaphor)
            r"\b(metaphorically|figuratively|symbolically)",
        ]
        
        # Common AI-generated metaphor templates (to detect)
        self.common_ai_metaphors = {
            "journey", "path", "road", "bridge", "foundation", "building",
            "key", "door", "window", "light", "darkness", "ocean", "wave"
        }
    
    def count(self, text: str, sentences: List[str]) -> Dict[str, Any]:
        """
        Count and analyze metaphors
        
        Args:
            text: Full cleaned text
            sentences: List of sentences
            
        Returns:
            Dictionary with metaphor metrics
        """
        text_lower = text.lower()
        
        # Detect potential metaphors
        metaphors = []
        for pattern in self.metaphor_patterns:
            matches = re.finditer(pattern, text_lower)
            metaphors.extend([m.group() for m in matches])
        
        # Count common AI metaphors (lower uniqueness score)
        common_count = sum(1 for word in self.common_ai_metaphors if word in text_lower)
        
        # Analyze uniqueness
        unique_metaphors = len(set(metaphors))
        total_metaphors = len(metaphors)
        uniqueness_ratio = unique_metaphors / max(1, total_metaphors)
        
        # Analyze distribution
        sentence_metaphors = [self._count_sentence_metaphors(s) for s in sentences]
        metaphor_variance = self._calculate_variance(sentence_metaphors) if len(sentence_metaphors) > 1 else 0.0
        
        # Score: higher uniqueness + higher variance = more human-like
        # Penalize common AI metaphors
        uniqueness_score = uniqueness_ratio
        common_penalty = min(1.0, common_count / max(1, total_metaphors)) if total_metaphors > 0 else 0.0
        variance_score = min(1.0, metaphor_variance / 2.0)
        
        # Combine scores
        metaphor_score = (
            uniqueness_score * 0.5 +
            (1.0 - common_penalty) * 0.3 +
            variance_score * 0.2
        )
        
        # If no metaphors detected, return neutral score
        if total_metaphors == 0:
            metaphor_score = 0.5
        
        return {
            "metaphor_score": float(metaphor_score),
            "total_metaphors": total_metaphors,
            "unique_metaphors": unique_metaphors,
            "uniqueness_ratio": float(uniqueness_ratio),
            "common_ai_metaphors": common_count,
            "metaphor_variance": float(metaphor_variance),
            "sentence_metaphors": sentence_metaphors
        }
    
    def _count_sentence_metaphors(self, sentence: str) -> int:
        """Count metaphors in a single sentence"""
        sentence_lower = sentence.lower()
        count = 0
        for pattern in self.metaphor_patterns:
            count += len(re.findall(pattern, sentence_lower))
        return count
    
    def _calculate_variance(self, values: List[int]) -> float:
        """Calculate variance of a list"""
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
