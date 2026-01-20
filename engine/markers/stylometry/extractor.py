"""
Stylometric Extractor
Extracts individual writing style fingerprint as a graph
"""

from typing import List, Dict, Any
import re
from collections import Counter


class StylometricExtractor:
    """
    Extracts stylometric features to create a writing fingerprint.
    Humans show more unique and consistent stylometric patterns.
    """
    
    def extract(self, text: str, sentences: List[str], tokens: List[str]) -> Dict[str, Any]:
        """
        Extract stylometric features
        
        Args:
            text: Full cleaned text
            sentences: List of sentences
            tokens: List of tokens
            
        Returns:
            Dictionary with stylometric metrics
        """
        # Character-level features
        char_features = self._extract_char_features(text)
        
        # Word-level features
        word_features = self._extract_word_features(tokens)
        
        # Sentence-level features
        sentence_features = self._extract_sentence_features(sentences)
        
        # Punctuation features
        punct_features = self._extract_punctuation_features(text)
        
        # Vocabulary richness
        vocab_features = self._extract_vocab_features(tokens)
        
        # Combine features into a fingerprint
        fingerprint = {
            **char_features,
            **word_features,
            **sentence_features,
            **punct_features,
            **vocab_features
        }
        
        # Calculate uniqueness score
        # More variation in features = more human-like
        uniqueness_score = self._calculate_uniqueness(fingerprint)
        
        return {
            "stylometry_score": float(uniqueness_score),
            "fingerprint": fingerprint,
            "char_features": char_features,
            "word_features": word_features,
            "sentence_features": sentence_features,
            "punct_features": punct_features,
            "vocab_features": vocab_features
        }
    
    def _extract_char_features(self, text: str) -> Dict[str, float]:
        """Extract character-level features"""
        if not text:
            return {}
        
        return {
            "avg_char_per_word": len(text) / max(1, len(text.split())),
            "uppercase_ratio": sum(1 for c in text if c.isupper()) / len(text),
            "digit_ratio": sum(1 for c in text if c.isdigit()) / len(text),
            "space_ratio": text.count(' ') / len(text),
        }
    
    def _extract_word_features(self, tokens: List[str]) -> Dict[str, float]:
        """Extract word-level features"""
        if not tokens:
            return {}
        
        word_lengths = [len(token) for token in tokens]
        return {
            "avg_word_length": sum(word_lengths) / len(word_lengths),
            "word_length_variance": sum((x - sum(word_lengths)/len(word_lengths))**2 for x in word_lengths) / len(word_lengths),
            "long_word_ratio": sum(1 for w in tokens if len(w) > 6) / len(tokens),
            "short_word_ratio": sum(1 for w in tokens if len(w) < 4) / len(tokens),
        }
    
    def _extract_sentence_features(self, sentences: List[str]) -> Dict[str, float]:
        """Extract sentence-level features"""
        if not sentences:
            return {}
        
        sentence_lengths = [len(s.split()) for s in sentences]
        return {
            "avg_sentence_length": sum(sentence_lengths) / len(sentence_lengths),
            "sentence_length_variance": sum((x - sum(sentence_lengths)/len(sentence_lengths))**2 for x in sentence_lengths) / len(sentence_lengths),
            "sentence_count": len(sentences),
        }
    
    def _extract_punctuation_features(self, text: str) -> Dict[str, float]:
        """Extract punctuation features"""
        punct_chars = ".,!?;:—()[]{}'\""
        punct_counts = {char: text.count(char) for char in punct_chars}
        total_chars = len(text)
        
        return {
            f"punct_{char}_ratio": count / max(1, total_chars)
            for char, count in punct_counts.items()
        }
    
    def _extract_vocab_features(self, tokens: List[str]) -> Dict[str, float]:
        """Extract vocabulary richness features"""
        if not tokens:
            return {}
        
        unique_tokens = len(set(tokens))
        token_counts = Counter(tokens)
        
        # Type-token ratio (vocabulary richness)
        ttr = unique_tokens / len(tokens)
        
        # Hapax legomena (words that appear only once)
        hapax_count = sum(1 for count in token_counts.values() if count == 1)
        hapax_ratio = hapax_count / len(tokens)
        
        return {
            "type_token_ratio": ttr,
            "hapax_ratio": hapax_ratio,
            "unique_tokens": unique_tokens,
            "total_tokens": len(tokens),
        }
    
    def _calculate_uniqueness(self, fingerprint: Dict[str, float]) -> float:
        """
        Calculate uniqueness score based on feature variance
        Higher variance in features = more unique = more human-like
        """
        if not fingerprint:
            return 0.5
        
        # Calculate coefficient of variation for numeric features
        values = [v for v in fingerprint.values() if isinstance(v, (int, float)) and v > 0]
        
        if not values or len(values) < 2:
            return 0.5
        
        mean = sum(values) / len(values)
        if mean == 0:
            return 0.5
        
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        cv = std_dev / mean  # Coefficient of variation
        
        # Normalize CV to 0-1 range
        uniqueness = min(1.0, cv / 2.0)
        
        return uniqueness
