.PHONY: install test test-backend test-frontend lint format build deploy

install:
	cd backend && pip install -e ".[dev]"
	cd frontend && npm install
	pre-commit install

backend-dev:
	cd backend && uvicorn src.main:app --reload

frontend-dev:
	cd frontend && npm run dev

test:
	cd backend && pytest tests/ -v --cov=src --cov-fail-under=90
	cd frontend && npm run test

test-backend:
	cd backend && pytest tests/ -v --cov=src --cov-fail-under=90

test-frontend:
	cd frontend && npm run test

lint:
	cd backend && black --check src/ && ruff check src/ && mypy src/ --strict
	cd frontend && npm run lint

format:
	cd backend && black src/ && ruff --fix src/

build:
	docker build -t cif-credit-backend backend/
	docker build -t cif-credit-frontend frontend/

deploy:
	kubectl apply -f infrastructure/k8s/

logs-backend:
	kubectl logs -f deployment/cif-credit-backend

logs-frontend:
	kubectl logs -f deployment/cif-credit-frontend
