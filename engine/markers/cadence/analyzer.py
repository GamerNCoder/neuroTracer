"""
Cadence Variability Analyzer
Measures the irregularity in sentence pacing - humans show more variance
"""

from typing import List, Dict, Any
import numpy as np
import statistics


class CadenceAnalyzer:
    """
    Analyzes cadence (pacing) variability in text.
    Human writing shows more irregular cadence than AI.
    """
    
    def analyze(self, sentences: List[str], tokens: List[str]) -> Dict[str, Any]:
        """
        Analyze cadence variability
        
        Args:
            sentences: List of sentence strings
            tokens: List of all tokens in text
            
        Returns:
            Dictionary with cadence metrics
        """
        if len(sentences) < 2:
            return {
                "cadence_score": 0.5,
                "sentence_length_variance": 0.0,
                "pause_variance": 0.0,
                "rhythm_score": 0.5
            }
        
        # Sentence length variance
        sentence_lengths = [len(s) for s in sentences]
        length_variance = np.var(sentence_lengths) if len(sentence_lengths) > 1 else 0.0
        
        # Word count variance
        word_counts = [len(s.split()) for s in sentences]
        word_variance = np.var(word_counts) if len(word_counts) > 1 else 0.0
        
        # Pause patterns (punctuation-based)
        pause_patterns = self._analyze_pause_patterns(sentences)
        pause_variance = np.var(pause_patterns) if len(pause_patterns) > 1 else 0.0
        
        # Rhythm score (coefficient of variation)
        rhythm_scores = self._calculate_rhythm(sentences)
        rhythm_variance = np.var(rhythm_scores) if len(rhythm_scores) > 1 else 0.0
        
        # Normalize variances (heuristic thresholds)
        normalized_length_var = min(1.0, length_variance / 2000.0)
        normalized_word_var = min(1.0, word_variance / 100.0)
        normalized_pause_var = min(1.0, pause_variance / 2.0)
        normalized_rhythm_var = min(1.0, rhythm_variance / 0.1)
        
        # Combine metrics (weighted average)
        cadence_score = (
            normalized_length_var * 0.3 +
            normalized_word_var * 0.3 +
            normalized_pause_var * 0.2 +
            normalized_rhythm_var * 0.2
        )
        
        return {
            "cadence_score": float(cadence_score),
            "sentence_length_variance": float(length_variance),
            "word_count_variance": float(word_variance),
            "pause_variance": float(pause_variance),
            "rhythm_score": float(np.mean(rhythm_scores)) if rhythm_scores else 0.5,
            "rhythm_variance": float(rhythm_variance)
        }
    
    def _analyze_pause_patterns(self, sentences: List[str]) -> List[float]:
        """Analyze punctuation-based pause patterns"""
        pause_scores = []
        for sentence in sentences:
            # Count various pause indicators
            pauses = (
                sentence.count(',') * 0.5 +
                sentence.count(';') * 1.0 +
                sentence.count(':') * 1.0 +
                sentence.count('—') * 1.5 +
                sentence.count('(') * 0.5
            )
            pause_scores.append(pauses)
        return pause_scores
    
    def _calculate_rhythm(self, sentences: List[str]) -> List[float]:
        """Calculate rhythm score for each sentence"""
        rhythm_scores = []
        for sentence in sentences:
            words = sentence.split()
            if len(words) < 2:
                rhythm_scores.append(0.5)
                continue
            
            # Simple rhythm: variation in word lengths
            word_lengths = [len(w) for w in words]
            if len(word_lengths) > 1:
                cv = statistics.stdev(word_lengths) / statistics.mean(word_lengths)
                rhythm_scores.append(cv)
            else:
                rhythm_scores.append(0.5)
        
        return rhythm_scores
