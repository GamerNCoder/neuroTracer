.PHONY: help setup dev-api dev-web dev-all test lint clean scrape-blogs scrape-1k build-dataset train-local tune-blogs

help:
	@echo "TraceNeuro Development Commands"
	@echo ""
	@echo "  make setup      - Run initial setup (install dependencies)"
	@echo "  make dev-api    - Start FastAPI server"
	@echo "  make dev-web    - Start Next.js web dashboard"
	@echo "  make dev-all    - Start API + web together"
	@echo "  make scrape-blogs - Scrape pre-2012 blogs (20×25 via Wayback)"
	@echo "  make scrape-1k    - One batch of 100 toward 1000-post corpus"
	@echo "  make build-dataset - Export dataset.jsonl + splits from manifest"
	@echo "  make train-local  - Train human vs AI calibration from blog corpus"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linters"
	@echo "  make clean      - Clean build artifacts"

setup:
	@./setup.sh

dev-api:
	@NEUROTRACER_ALLOW_LOCAL_PATHS=1 NEUROTRACER_LOCAL_PATH_ROOT="$(CURDIR)/data/human" \
		cd api && uvicorn main:app --reload --host 127.0.0.1 --port 8000

dev-web:
	@cd web && npm run dev

dev-all:
	@chmod +x scripts/dev_all.sh && ./scripts/dev_all.sh

scrape-blogs:
	@python3 scripts/scrape_pre2012_blogs.py

scrape-1k:
	@python3 scripts/scrape_batches.py --target 1000 --batch-size 100 --extended --once

build-dataset:
	@python3 scripts/build_local_dataset.py

train-local:
	@python3 scripts/train_from_blogs.py

tune-blogs:
	@python3 scripts/train_from_blogs.py && python3 scripts/evaluate_corpus.py

test:
	@pytest tests/ -v

lint:
	@black . --check
	@flake8 .

clean:
	@find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@rm -rf .pytest_cache
	@rm -rf web/.next
	@rm -rf web/node_modules

