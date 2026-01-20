.PHONY: help setup dev-api dev-web test lint clean

help:
	@echo "TraceNeuro Development Commands"
	@echo ""
	@echo "  make setup      - Run initial setup (install dependencies)"
	@echo "  make dev-api    - Start FastAPI server"
	@echo "  make dev-web    - Start Next.js web dashboard"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linters"
	@echo "  make clean      - Clean build artifacts"

setup:
	@./setup.sh

dev-api:
	@cd api && uvicorn main:app --reload --host 0.0.0.0 --port 8000

dev-web:
	@cd web && npm run dev

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

