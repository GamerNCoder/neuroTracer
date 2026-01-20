"""
Feature Encoder
Converts text and markers into numerical vectors for analysis
"""

from typing import List, Dict, Any, Optional
import numpy as np


class FeatureEncoder:
    """
    Encodes text and cognitive markers into numerical feature vectors.
    Supports both simple feature extraction and embeddings.
    """
    
    def __init__(self, use_embeddings: bool = False):
        """
        Initialize feature encoder
        
        Args:
            use_embeddings: Whether to use sentence-transformers (requires model download)
        """
        self.use_embeddings = use_embeddings
        self.embedding_model = None
        
        if use_embeddings:
            # Lazy load embedding model
            self._load_embedding_model()
    
    def encode_text(self, text: str) -> np.ndarray:
        """
        Encode text into feature vector
        
        Args:
            text: Input text
            
        Returns:
            Feature vector as numpy array
        """
        if self.use_embeddings and self.embedding_model:
            return self._encode_with_embeddings(text)
        else:
            return self._encode_simple_features(text)
    
    def encode_sentences(self, sentences: List[str]) -> np.ndarray:
        """
        Encode multiple sentences into feature matrix
        
        Args:
            sentences: List of sentence strings
            
        Returns:
            Feature matrix (n_sentences, n_features)
        """
        if self.use_embeddings and self.embedding_model:
            return np.array([self._encode_with_embeddings(s) for s in sentences])
        else:
            return np.array([self._encode_simple_features(s) for s in sentences])
    
    def encode_markers(self, marker_data: Dict[str, Any]) -> np.ndarray:
        """
        Encode cognitive marker data into feature vector
        
        Args:
            marker_data: Dictionary with marker scores and metrics
            
        Returns:
            Feature vector
        """
        features = []
        
        # Extract numeric values from marker data
        for key, value in marker_data.items():
            if isinstance(value, (int, float)):
                features.append(value)
            elif isinstance(value, dict):
                # Recursively extract from nested dicts
                features.extend(self._extract_numeric_values(value))
            elif isinstance(value, list):
                # Average list values
                if value and all(isinstance(x, (int, float)) for x in value):
                    features.append(np.mean(value))
        
        return np.array(features) if features else np.array([0.0])
    
    def _encode_simple_features(self, text: str) -> np.ndarray:
        """
        Encode text using simple statistical features
        (Fallback when embeddings not available)
        """
        words = text.split()
        chars = list(text)
        
        features = [
            len(text),  # Total length
            len(words),  # Word count
            len(set(words)) / max(1, len(words)),  # Type-token ratio
            sum(len(w) for w in words) / max(1, len(words)),  # Avg word length
            text.count('.'),  # Period count
            text.count(','),  # Comma count
            text.count('?'),  # Question count
            text.count('!'),  # Exclamation count
            sum(1 for c in chars if c.isupper()) / max(1, len(chars)),  # Uppercase ratio
            sum(1 for c in chars if c.isdigit()) / max(1, len(chars)),  # Digit ratio
        ]
        
        return np.array(features)
    
    def _encode_with_embeddings(self, text: str) -> np.ndarray:
        """
        Encode text using sentence-transformers embeddings
        TODO: Implement with sentence-transformers library
        """
        # Placeholder - will use sentence-transformers when implemented
        # For now, fall back to simple features
        return self._encode_simple_features(text)
    
    def _load_embedding_model(self):
        """Lazy load sentence-transformers model"""
        try:
            # TODO: Uncomment when ready to use embeddings
            # from sentence_transformers import SentenceTransformer
            # self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            pass
        except ImportError:
            print("Warning: sentence-transformers not installed, using simple features")
            self.use_embeddings = False
    
    def _extract_numeric_values(self, data: Dict[str, Any]) -> List[float]:
        """Recursively extract numeric values from nested dictionaries"""
        values = []
        for key, value in data.items():
            if isinstance(value, (int, float)):
                values.append(value)
            elif isinstance(value, dict):
                values.extend(self._extract_numeric_values(value))
            elif isinstance(value, list):
                if value and all(isinstance(x, (int, float)) for x in value):
                    values.append(np.mean(value))
        return values
