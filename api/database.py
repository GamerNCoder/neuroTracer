"""
Database models and setup for scoring history
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class ScoringHistory(Base):
    """Model for storing scoring history"""
    __tablename__ = "scoring_history"
    
    id = Column(Integer, primary_key=True, index=True)
    text_hash = Column(String, index=True)  # Hash of text for deduplication
    text_preview = Column(String(500))  # First 500 chars
    humanscore = Column(Float)
    breakdown = Column(JSON)  # Store marker breakdown as JSON
    full_metadata = Column(JSON)  # Store full metadata as JSON (renamed from 'metadata' - SQLAlchemy reserved)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ScoringHistory(id={self.id}, humanscore={self.humanscore})>"


# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./traceneuro.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
