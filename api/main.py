"""
TraceNeuro API - Main FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import scoring, history
from api.database import init_db

app = FastAPI(
    title="TraceNeuro API",
    description="Cognitive Authenticity Engine - Human Cognition Fingerprint Detection",
    version="0.1.0",
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(scoring.router, prefix="/api/v1", tags=["scoring"])
app.include_router(history.router, prefix="/api/v1", tags=["history"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "TraceNeuro API",
        "version": "0.1.0"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "TraceNeuro API",
        "version": "0.1.0",
        "endpoints": {
            "score": "/api/v1/score",
            "health": "/health"
        }
    }

