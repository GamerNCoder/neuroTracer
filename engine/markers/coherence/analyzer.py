"""
Coherence Break Analyzer
Detects mid-thought direction changes and coherence breaks
Humans show more irregular coherence patterns
"""

from typing import List, Dict, Any
import re


class CoherenceAnalyzer:
    """
    Analyzes coherence breaks - sudden topic shifts or mid-thought changes.
    Humans show more irregular coherence than AI.
    """
    
    def __init__(self):
        # Discourse markers that indicate breaks
        self.break_markers = [
            r"\b(but|however|although|though|yet)",
            r"\b(actually|wait|hold\s+on|hmm|well)",
            r"\b(let\s+me\s+think|actually|come\s+to\s+think)",
            r"\b(on\s+second\s+thought|then\s+again)",
            r"\b(nevermind|scratch\s+that)",
        ]
        
        # Topic shift indicators
        self.topic_shift_markers = [
            r"\b(speaking\s+of|by\s+the\s+way|incidentally)",
            r"\b(that\s+reminds\s+me|oh\s+yeah)",
            r"\b(changing\s+the\s+subject|anyway)",
        ]
    
    def analyze(self, sentences: List[str]) -> Dict[str, Any]:
        """
        Analyze coherence breaks
        
        Args:
            sentences: List of sentence strings
            
        Returns:
            Dictionary with coherence metrics
        """
        if len(sentences) < 2:
            return {
                "coherence_score": 0.5,
                "break_count": 0,
                "topic_shifts": 0,
                "coherence_variance": 0.0
            }
        
        # Count breaks in each sentence
        sentence_breaks = []
        total_breaks = 0
        topic_shifts = 0
        
        for i, sentence in enumerate(sentences):
            breaks = self._count_breaks(sentence)
            sentence_breaks.append(breaks)
            total_breaks += breaks
            
            # Check for topic shifts
            if self._has_topic_shift(sentence):
                topic_shifts += 1
        
        # Calculate variance in breaks
        break_variance = self._calculate_variance(sentence_breaks) if len(sentence_breaks) > 1 else 0.0
        
        # Analyze sentence transitions
        transition_scores = self._analyze_transitions(sentences)
        transition_variance = self._calculate_variance(transition_scores) if len(transition_scores) > 1 else 0.0
        
        # Score: more breaks + higher variance = more human-like
        # But too many breaks might indicate poor writing, so normalize
        break_density = total_breaks / max(1, len(sentences))
        break_score = min(1.0, break_density / 2.0)  # Normalize
        
        variance_score = min(1.0, (break_variance + transition_variance) / 4.0)
        
        # Topic shifts are strong human indicators
        shift_score = min(1.0, topic_shifts / max(1, len(sentences) / 5))
        
        coherence_score = (
            break_score * 0.4 +
            variance_score * 0.4 +
            shift_score * 0.2
        )
        
        return {
            "coherence_score": float(coherence_score),
            "break_count": total_breaks,
            "topic_shifts": topic_shifts,
            "break_density": float(break_density),
            "coherence_variance": float(break_variance),
            "transition_variance": float(transition_variance),
            "sentence_breaks": sentence_breaks
        }
    
    def _count_breaks(self, sentence: str) -> int:
        """Count coherence break markers in a sentence"""
        sentence_lower = sentence.lower()
        count = 0
        for pattern in self.break_markers:
            count += len(re.findall(pattern, sentence_lower))
        return count
    
    def _has_topic_shift(self, sentence: str) -> bool:
        """Check if sentence contains topic shift markers"""
        sentence_lower = sentence.lower()
        for pattern in self.topic_shift_markers:
            if re.search(pattern, sentence_lower):
                return True
        return False
    
    def _analyze_transitions(self, sentences: List[str]) -> List[float]:
        """Analyze smoothness of transitions between sentences"""
        if len(sentences) < 2:
            return [0.5]
        
        transition_scores = []
        for i in range(len(sentences) - 1):
            # Simple heuristic: check for explicit transition words
            # More explicit transitions = smoother (more AI-like)
            # Fewer explicit transitions = more abrupt (more human-like)
            next_sentence = sentences[i + 1].lower()
            transition_words = [
                "furthermore", "moreover", "additionally", "in addition",
                "therefore", "thus", "hence", "consequently",
                "first", "second", "finally", "next", "then"
            ]
            has_transition = any(word in next_sentence for word in transition_words)
            # Lower score = more abrupt = more human-like
            transition_scores.append(0.3 if has_transition else 0.7)
        
        return transition_scores
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list"""
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance
