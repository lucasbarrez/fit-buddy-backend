# Makefile for Oh My Match Backend

.PHONY: help install dev test lint format clean docker-build docker-up docker-down

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies with UV
	uv pip install -r pyproject.toml
	uv pip install pytest pytest-asyncio pytest-cov httpx ruff black mypy pre-commit

dev: ## Run development server
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## Run tests
	pytest -v

test-cov: ## Run tests with coverage
	pytest --cov=app --cov-report=html --cov-report=term

lint: ## Run linting
	ruff check app tests
	mypy app

format: ## Format code
	black app tests
	ruff check --fix app tests

format-check: ## Check code formatting
	black --check app tests
	ruff check app tests

clean: ## Clean cache files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	rm -rf htmlcov
	rm -rf .coverage

docker-build: ## Build Docker image for development
	docker-compose build

docker-up: ## Start Docker containers for development
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

docker-logs: ## Show Docker logs
	docker-compose logs -f

docker-build-prod: ## Build Docker image for production
	docker-compose -f docker-compose.prod.yml build

docker-up-prod: ## Start Docker containers for production
	docker-compose -f docker-compose.prod.yml up -d

docker-down-prod: ## Stop production Docker containers
	docker-compose -f docker-compose.prod.yml down

setup: ## Initial setup
	chmod +x setup.sh
	./setup.sh

pre-commit: ## Install pre-commit hooks
	pre-commit install
	pre-commit run --all-files
