# Quick Start Guide

## Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

## Setup

1. **Clone and navigate to the repository**
   ```bash
   cd neurotracer
   ```

2. **Run the setup script**
   ```bash
   ./setup.sh
   ```
   
   Or manually:
   ```bash
   # Python environment
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Node dependencies
   cd web && npm install && cd ..
   ```

3. **Start the API server**
   ```bash
   # Option 1: Using Make
   make dev-api
   
   # Option 2: Direct command
   cd api && uvicorn main:app --reload
   ```
   
   API will be available at `http://localhost:8000`

4. **Start the web dashboard** (in a new terminal)
   ```bash
   # Option 1: Using Make
   make dev-web
   
   # Option 2: Direct command
   cd web && npm run dev
   ```
   
   Dashboard will be available at `http://localhost:3000`

## Testing the API

### Using curl

```bash
curl -X POST http://localhost:8000/api/v1/score \
  -H "Content-Type: application/json" \
  -d '{
    "text": "I think maybe we should reconsider this approach. It seems like there might be a better way, but I'm not entirely sure. Let me think about it...",
    "options": {}
  }'
```

### Using the web interface

1. Navigate to `http://localhost:3000`
2. Paste or type text in the textarea
3. Click "Analyze Text"
4. View the HumanScore™ and breakdown

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v
```

## Project Structure

```
neurotracer/
├── api/              # FastAPI backend
├── engine/           # Core cognitive marker engines
├── web/              # Next.js frontend
├── data/             # Training/test data
├── docs/             # Documentation
└── tests/            # Test suite
```

## Next Steps

1. **Implement cognitive markers** - Start with `engine/markers/` modules
2. **Collect training data** - Add samples to `data/human/` and `data/ai/`
3. **Tune weights** - Adjust marker weights in `engine/humanscore/scorer.py`
4. **Add authentication** - Implement auth in `api/auth/`
5. **Build reporting** - Create detailed reports in `api/report/`

## Troubleshooting

**Port already in use:**
- Change API port: `uvicorn main:app --port 8001`
- Change web port: `npm run dev -- -p 3001`

**Python import errors:**
- Ensure virtual environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

**Node module errors:**
- Clear cache: `rm -rf web/node_modules web/.next && cd web && npm install`

