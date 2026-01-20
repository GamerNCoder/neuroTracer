# Architecture Overview

## System Design

TraceNeuro follows a modular, microservices-inspired architecture optimized for cognitive marker analysis.

### Core Components

1. **Preprocessing Layer** (`engine/preprocessing/`)
   - Text cleaning and normalization
   - Sentence segmentation
   - Tokenization
   - Prepares text for marker extraction

2. **Cognitive Marker Extractors** (`engine/markers/`)
   - **Drift**: Semantic drift vector analysis
   - **Cadence**: Sentence pacing variability
   - **Hedging**: Uncertainty and hedging language patterns
   - **Metaphor**: Metaphor rarity and uniqueness
   - **Coherence**: Discourse coherence break detection
   - **Stylometry**: Individual writing style fingerprint

3. **Fusion Engine** (`engine/fusion/`)
   - Weighted combination of markers
   - Normalization and calibration
   - Hybrid detection logic

4. **HumanScore Engine** (`engine/humanscore/`)
   - Final score calculation
   - Confidence intervals
   - Report generation

5. **API Layer** (`api/`)
   - RESTful endpoints
   - Authentication (future)
   - Rate limiting (future)
   - Request/response validation

6. **Web Dashboard** (`web/`)
   - Next.js frontend
   - Real-time scoring
   - Visualization components
   - History and reports

## Data Flow

```
User Input
    ↓
API Gateway (FastAPI)
    ↓
Text Processor (cleaning, segmentation)
    ↓
┌─────────────────────────────────────┐
│  Parallel Marker Extraction         │
│  - Drift Analysis                    │
│  - Cadence Calculation               │
│  - Hedging Detection                 │
│  - Metaphor Analysis                  │
│  - Coherence Break Detection         │
│  - Stylometric Graph                 │
└─────────────────────────────────────┘
    ↓
Feature Encoder (embeddings, vectors)
    ↓
Fusion Layer (weighted combination)
    ↓
HumanScore Engine (final score)
    ↓
Report Builder (breakdown, metadata)
    ↓
API Response / Dashboard Display
```

## Marker Implementation Status

| Marker | Status | Priority |
|--------|--------|----------|
| Drift | 🔴 Placeholder | High |
| Cadence | 🟡 Partial | High |
| Hedging | 🟡 Partial | High |
| Metaphor | 🔴 Placeholder | Medium |
| Coherence | 🔴 Placeholder | High |
| Stylometry | 🔴 Placeholder | High |

## Technology Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Next.js (TypeScript/React)
- **NLP**: spaCy, NLTK, Transformers
- **ML**: scikit-learn, NumPy, SciPy
- **Embeddings**: sentence-transformers

## Future Enhancements

1. **Database Layer**: SQLAlchemy + PostgreSQL for history
2. **Caching**: Redis for performance
3. **Authentication**: JWT-based auth
4. **Model Fine-tuning**: Custom models on collected data
5. **Real-time Processing**: WebSocket support
6. **Batch Processing**: Async job queue

