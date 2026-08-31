.PHONY: install test test-backend test-frontend lint format build migrate db-up \
        artifacts-init deploy

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

artifacts-init:
	python mlops/scripts/init_artifacts.py

migrate:
	cd backend && alembic upgrade head

db-up:
	docker compose -f infrastructure/docker/docker-compose.yml up -d db

build:
	# Contexte = racine du repo (les Dockerfiles y referent backend/, mlops/)
	docker build -f backend/Dockerfile.api -t cif-credit-backend .
	docker build -f frontend/Dockerfile.frontend -t cif-credit-frontend .

deploy:
	# Deploiement Docker Compose sur le serveur cible (AWS EC2 / VPS)
	docker compose -f infrastructure/docker/docker-compose.prod.yml up -d --build
