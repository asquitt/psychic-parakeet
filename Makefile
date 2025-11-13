# Makefile for ML Pipeline
#
# This Makefile provides convenient commands for common development tasks
# Usage: make <command>

.PHONY: help install test lint format clean docker-up docker-down train serve monitor docs

# Default target
.DEFAULT_GOAL := help

# ============================================================================
# Help
# ============================================================================
help:  ## Show this help message
	@echo "ML Pipeline - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ============================================================================
# Setup
# ============================================================================
install:  ## Install dependencies
	pip install -r requirements.txt
	pip install -e .

install-dev:  ## Install development dependencies
	pip install -r requirements.txt
	pip install -e ".[dev]"

# ============================================================================
# Code Quality
# ============================================================================
lint:  ## Run linters
	flake8 src/ --max-line-length=120 --extend-ignore=E203,W503
	mypy src/ --ignore-missing-imports

format:  ## Format code with black and isort
	black src/
	isort src/

format-check:  ## Check code formatting
	black --check src/
	isort --check-only src/

# ============================================================================
# Testing
# ============================================================================
test:  ## Run tests
	pytest tests/ -v

test-cov:  ## Run tests with coverage
	pytest tests/ -v --cov=ml_pipeline --cov-report=html --cov-report=term

# ============================================================================
# Docker
# ============================================================================
docker-build:  ## Build Docker images
	docker-compose build

docker-up:  ## Start all services
	docker-compose up -d
	@echo "Services starting..."
	@echo "MLflow UI: http://localhost:5000"
	@echo "Prefect UI: http://localhost:4200"
	@echo "Model API: http://localhost:8000/docs"
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana: http://localhost:3000"

docker-down:  ## Stop all services
	docker-compose down

docker-logs:  ## View logs
	docker-compose logs -f

docker-clean:  ## Clean up Docker resources
	docker-compose down -v
	docker system prune -f

# ============================================================================
# ML Pipeline Operations
# ============================================================================
train:  ## Run training pipeline
	python scripts/run_training.py

serve:  ## Start model serving API
	uvicorn ml_pipeline.serving.api:app --reload --host 0.0.0.0 --port 8000

monitor:  ## Run monitoring pipeline
	python scripts/run_monitoring.py

# ============================================================================
# Development
# ============================================================================
notebook:  ## Start Jupyter notebook
	jupyter notebook notebooks/

clean:  ## Clean up temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info

docs:  ## Generate documentation
	@echo "Documentation available in docs/ and README.md"

# ============================================================================
# Data
# ============================================================================
generate-sample-data:  ## Generate sample data for testing
	python scripts/generate_sample_data.py
