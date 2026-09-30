.PHONY: install dev api web test lint

install:
	python3.13 -m venv .venv
	.venv/bin/pip install -r api/requirements.txt -r api/requirements-dev.txt
	cd web && npm ci

# Runs FastAPI on :8000 and Next.js on :3000 (Next proxies /api to FastAPI)
dev:
	$(MAKE) -j2 api web

api:
	cd api && set -a && { [ -f ../.env ] && . ../.env || true; } && set +a && ../.venv/bin/uvicorn index:app --reload --port 8000

web:
	cd web && API_ORIGIN=http://127.0.0.1:8000 npm run dev

test:
	cd api && ../.venv/bin/pytest -q

lint:
	cd api && ../.venv/bin/ruff check .
	cd web && npm run lint && npx tsc --noEmit
