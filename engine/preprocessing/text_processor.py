"""
Text Preprocessing Pipeline
Handles cleaning, segmentation, and tokenization
"""

import re
from typing import List, Dict, Any


class TextProcessor:
    """Processes raw text for cognitive marker analysis"""
    
    def __init__(self):
        self.min_sentence_length = 3
        self.max_sentence_length = 500
    
    def process(self, text: str) -> Dict[str, Any]:
        """
        Main processing pipeline
        
        Args:
            text: Raw input text
            
        Returns:
            Dictionary with processed text components
        """
        cleaned = self.clean(text)
        sentences = self.segment_sentences(cleaned)
        tokens = self.tokenize(cleaned)
        
        return {
            "original": text,
            "cleaned": cleaned,
            "sentences": sentences,
            "tokens": tokens,
            "sentence_count": len(sentences),
            "token_count": len(tokens),
            "char_count": len(cleaned)
        }
    
    def clean(self, text: str) -> str:
        """Remove artifacts and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove URLs (keep structure)
        text = re.sub(r'http[s]?://\S+', '[URL]', text)
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace("'", "'").replace("'", "'")
        
        # Remove excessive punctuation (keep sentence structure)
        text = re.sub(r'[.]{3,}', '...', text)
        
        return text.strip()
    
    def segment_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting (can be enhanced with NLTK/spaCy)
        sentences = re.split(r'[.!?]+', text)
        
        # Filter and clean sentences
        sentences = [
            s.strip() 
            for s in sentences 
            if len(s.strip()) >= self.min_sentence_length
            and len(s.strip()) <= self.max_sentence_length
        ]
        
        return sentences
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        # Simple tokenization (can be enhanced)
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens

