#!/usr/bin/env bash
# Start TraceNeuro API (8000) and Next.js web (3000). Ctrl+C stops both.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -d venv ]]; then
  echo "Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi
# shellcheck disable=SC1091
source venv/bin/activate

if [[ ! -d web/node_modules ]]; then
  echo "Installing web dependencies..."
  (cd web && npm install)
fi

cleanup() {
  kill "$API_PID" "$WEB_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

export NEUROTRACER_ALLOW_LOCAL_PATHS=1
export NEUROTRACER_LOCAL_PATH_ROOT="$ROOT/data/human"
echo "Starting API on http://127.0.0.1:8000 (local batch paths enabled)"
(cd api && uvicorn main:app --reload --host 127.0.0.1 --port 8000) &
API_PID=$!

echo "Starting web on http://127.0.0.1:3000"
(cd web && npm run dev -- -p 3000 -H 127.0.0.1) &
WEB_PID=$!

sleep 3
if curl -sf http://127.0.0.1:8000/health >/dev/null; then
  echo "API healthy"
else
  echo "Warning: API not responding yet — check logs above"
fi

echo "Open http://127.0.0.1:3000 — press Ctrl+C to stop"
wait
