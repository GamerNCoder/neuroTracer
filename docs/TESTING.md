# Testing TraceNeuro locally

## Quick start (two terminals)

```bash
cd arnav/neurotracer
source venv/bin/activate
make dev-all   # API :8000 + web :3000
```

Or separately: `make dev-api` and `make dev-web`.

- API docs: http://localhost:8000/docs  
- Dashboard: http://localhost:3000  

## Automated tests

```bash
source venv/bin/activate
make test
```

## Manual API test

```bash
curl -s http://localhost:8000/health | python3 -m json.tool

curl -s -X POST http://localhost:8000/api/v1/score \
  -H "Content-Type: application/json" \
  -d '{"text":"I have been thinking about this for a while. Maybe we should try again. Honestly I am not sure — wait, actually let me explain it differently. Sometimes the weather changes everything."}' \
  | python3 -m json.tool
```

Expect `calibrated: true` if `data/models/calibration.json` exists.

## Blog corpus batch test

```bash
export NEUROTRACER_ALLOW_LOCAL_PATHS=1
export NEUROTRACER_LOCAL_PATH_ROOT="$(pwd)/data/human"
python3 scripts/batch_score_path.py data/human/blogs-pre2012 --limit 5
```

## Re-train / tune on blog corpus

```bash
make tune-blogs    # train + print corpus eval (target ~88% likely_human on blogs)
make train-local   # train only
python3 scripts/evaluate_corpus.py
```

Restart the API after retraining so it reloads `data/models/calibration.json`.
