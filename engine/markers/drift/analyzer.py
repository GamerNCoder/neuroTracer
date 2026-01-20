"""
Semantic Drift Analyzer
Tracks meaning changes across sentences to detect human thought patterns
"""

from typing import List, Dict, Any
import numpy as np


class DriftAnalyzer:
    """
    Analyzes semantic drift - how meaning evolves across sentences.
    Humans show more irregular drift patterns than AI.
    """
    
    def __init__(self):
        # Placeholder for embedding model (will use sentence-transformers)
        self.embedding_model = None
    
    def analyze(self, sentences: List[str]) -> Dict[str, Any]:
        """
        Analyze semantic drift across sentences
        
        Args:
            sentences: List of sentence strings
            
        Returns:
            Dictionary with drift metrics
        """
        if len(sentences) < 2:
            return {
                "drift_score": 0.5,
                "drift_variance": 0.0,
                "drift_vectors": [],
                "mean_drift": 0.0
            }
        
        # Calculate drift vectors (placeholder - will use embeddings)
        drift_vectors = self._calculate_drift_vectors(sentences)
        
        if not drift_vectors:
            return {
                "drift_score": 0.5,
                "drift_variance": 0.0,
                "drift_vectors": [],
                "mean_drift": 0.0
            }
        
        # Calculate metrics
        drift_magnitudes = [np.linalg.norm(dv) for dv in drift_vectors]
        mean_drift = np.mean(drift_magnitudes)
        drift_variance = np.var(drift_magnitudes)
        
        # Higher variance in drift = more human-like
        # Normalize variance (heuristic threshold)
        normalized_variance = min(1.0, drift_variance / 0.1)
        
        # Combine mean and variance for final score
        drift_score = (normalized_variance * 0.6 + min(1.0, mean_drift) * 0.4)
        
        return {
            "drift_score": float(drift_score),
            "drift_variance": float(drift_variance),
            "drift_vectors": [dv.tolist() if isinstance(dv, np.ndarray) else dv for dv in drift_vectors],
            "mean_drift": float(mean_drift)
        }
    
    def _calculate_drift_vectors(self, sentences: List[str]) -> List[np.ndarray]:
        """
        Calculate semantic drift vectors between consecutive sentences
        
        TODO: Replace with actual sentence embeddings using sentence-transformers
        For now, returns placeholder vectors based on simple features
        """
        if len(sentences) < 2:
            return []
        
        drift_vectors = []
        
        # Placeholder: simple feature-based drift
        # In production, this will use sentence embeddings
        prev_features = self._extract_simple_features(sentences[0])
        
        for sentence in sentences[1:]:
            curr_features = self._extract_simple_features(sentence)
            # Drift vector = difference in features
            drift = np.array(curr_features) - np.array(prev_features)
            drift_vectors.append(drift)
            prev_features = curr_features
        
        return drift_vectors
    
    def _extract_simple_features(self, sentence: str) -> List[float]:
        """
        Extract simple features for placeholder implementation
        TODO: Replace with proper sentence embeddings
        """
        words = sentence.lower().split()
        return [
            len(sentence),  # Length
            len(words),  # Word count
            sum(1 for c in sentence if c.isupper()) / max(1, len(sentence)),  # Capitalization ratio
            sentence.count('?') + sentence.count('!'),  # Question/exclamation count
        ]
