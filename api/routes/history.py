"""
Scoring History API Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import hashlib

from api.database import get_db, ScoringHistory
from pydantic import BaseModel

router = APIRouter()


class HistoryResponse(BaseModel):
    """Response model for scoring history"""
    id: int
    text_preview: str
    humanscore: float
    breakdown: dict
    created_at: datetime


@router.get("/history", response_model=List[HistoryResponse])
async def get_scoring_history(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get scoring history
    
    Args:
        limit: Maximum number of records to return
        offset: Number of records to skip
        
    Returns:
        List of scoring history records
    """
    records = db.query(ScoringHistory)\
        .order_by(ScoringHistory.created_at.desc())\
        .offset(offset)\
        .limit(limit)\
        .all()
    
    return [
        HistoryResponse(
            id=r.id,
            text_preview=r.text_preview,
            humanscore=r.humanscore,
            breakdown=r.breakdown,
            created_at=r.created_at
        )
        for r in records
    ]


@router.get("/history/{record_id}", response_model=HistoryResponse)
async def get_scoring_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific scoring record by ID
    
    Args:
        record_id: ID of the record
        
    Returns:
        Scoring history record
    """
    record = db.query(ScoringHistory).filter(ScoringHistory.id == record_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return HistoryResponse(
        id=record.id,
        text_preview=record.text_preview,
        humanscore=record.humanscore,
        breakdown=record.breakdown,
        created_at=record.created_at
    )


def save_scoring_history(
    text: str,
    humanscore: float,
    breakdown: dict,
    metadata: dict,
    db: Session
) -> ScoringHistory:
    """
    Save scoring result to history
    
    Args:
        text: Original text
        humanscore: Calculated HumanScore
        breakdown: Marker breakdown
        metadata: Full metadata
        db: Database session
        
    Returns:
        Created ScoringHistory record
    """
    # Create text hash for deduplication
    text_hash = hashlib.sha256(text.encode()).hexdigest()
    text_preview = text[:500] if len(text) > 500 else text
    
    # Check if record already exists (optional - can allow duplicates)
    # existing = db.query(ScoringHistory).filter(ScoringHistory.text_hash == text_hash).first()
    # if existing:
    #     return existing
    
    # Create new record
    record = ScoringHistory(
        text_hash=text_hash,
        text_preview=text_preview,
        humanscore=humanscore,
        breakdown=breakdown,
        full_metadata=metadata
    )
    
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return record
