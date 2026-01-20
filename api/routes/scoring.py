"""
Scoring API Routes
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from engine.preprocessing.text_processor import TextProcessor
from engine.humanscore.scorer import HumanScoreEngine
from api.database import get_db
from api.routes.history import save_scoring_history

router = APIRouter()


class ScoreRequest(BaseModel):
    """Request model for text scoring"""
    text: str = Field(..., min_length=10, description="Text to analyze")
    options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional scoring parameters"
    )


class ScoreResponse(BaseModel):
    """Response model for text scoring"""
    humanscore: float = Field(..., ge=0.0, le=1.0, description="HumanScore (0-1)")
    breakdown: Dict[str, float] = Field(..., description="Per-marker breakdown")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")


@router.post("/score", response_model=ScoreResponse)
async def score_text(
    request: ScoreRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze text and return HumanScore™ with cognitive marker breakdown.
    
    Returns a score between 0 (AI-generated) and 1 (human-written),
    along with detailed breakdown of cognitive markers.
    """
    try:
        # Preprocess text
        processor = TextProcessor()
        processed = processor.process(request.text)
        
        # Calculate HumanScore
        scorer = HumanScoreEngine()
        result = scorer.score(processed)
        
        # Save to history
        save_scoring_history(
            text=request.text,
            humanscore=result["humanscore"],
            breakdown=result["breakdown"],
            metadata=result["metadata"],
            db=db
        )
        
        return ScoreResponse(
            humanscore=result["humanscore"],
            breakdown=result["breakdown"],
            metadata=result["metadata"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")

