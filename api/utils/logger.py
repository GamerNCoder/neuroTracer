"""
JSONL Logging Utility
Logs scoring requests and results to JSONL file for later ingestion
"""

import json
import os
from datetime import datetime
from typing import Dict, Any
from pathlib import Path


class JSONLLogger:
    """Logger that writes to JSONL (JSON Lines) format"""
    
    def __init__(self, log_file: str = "logs/scoring_logs.jsonl"):
        """
        Initialize JSONL logger
        
        Args:
            log_file: Path to log file (relative to project root)
        """
        self.log_file = log_file
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        """Ensure log directory exists"""
        log_path = Path(self.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log_scoring_request(
        self,
        text: str,
        result: Dict[str, Any],
        request_options: Dict[str, Any] = None,
        error: str = None
    ):
        """
        Log a scoring request and result to JSONL file
        
        Args:
            text: Input text that was analyzed
            result: Scoring result dictionary
            request_options: Optional request options
            error: Optional error message if request failed
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "text": text,
            "text_length": len(text),
            "text_hash": self._hash_text(text),
            "result": result if not error else None,
            "error": error,
            "request_options": request_options or {},
        }
        
        self._write_log_entry(log_entry)
    
    def _hash_text(self, text: str) -> str:
        """Generate hash of text for deduplication"""
        import hashlib
        return hashlib.sha256(text.encode()).hexdigest()
    
    def _write_log_entry(self, entry: Dict[str, Any]):
        """
        Write a single log entry as a JSON line
        
        Args:
            entry: Dictionary to write as JSON line
        """
        try:
            # Get absolute path
            project_root = Path(__file__).parent.parent.parent
            log_path = project_root / self.log_file
            
            # Append to file (JSONL format - one JSON object per line)
            with open(log_path, "a", encoding="utf-8") as f:
                json_line = json.dumps(entry, ensure_ascii=False)
                f.write(json_line + "\n")
        except Exception as e:
            # Don't fail the request if logging fails
            print(f"Warning: Failed to write log entry: {e}")


# Global logger instance
_logger_instance = None


def get_logger() -> JSONLLogger:
    """Get or create global logger instance"""
    global _logger_instance
    if _logger_instance is None:
        log_file = os.getenv("SCORING_LOG_FILE", "logs/scoring_logs.jsonl")
        _logger_instance = JSONLLogger(log_file)
    return _logger_instance
