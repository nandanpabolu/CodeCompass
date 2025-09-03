.PHONY: help install install-dev test lint format clean run-server run-dashboard setup

help: ## Show this help message
	@echo "CodeCompass - MCP Codebase Assistant"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

test: ## Run tests
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

lint: ## Run linting
	flake8 src/ tests/
	mypy src/

format: ## Format code
	black src/ tests/
	isort src/ tests/

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

setup: ## Set up development environment
	@echo "Setting up CodeCompass development environment..."
	python -m venv venv
	@echo "Virtual environment created. Please activate it with:"
	@echo "  source venv/bin/activate  # On Unix/macOS"
	@echo "  venv\\Scripts\\activate     # On Windows"
	@echo "Then run: make install-dev"

run-server: ## Run MCP server
	python src/mcp_server.py

run-dashboard: ## Run Streamlit dashboard
	streamlit run src/streamlit_app.py

run-both: ## Run both server and dashboard
	@echo "Starting MCP server in background..."
	python src/mcp_server.py &
	@echo "Starting Streamlit dashboard..."
	streamlit run src/streamlit_app.py

check: ## Run all checks (lint, test, format)
	@echo "Running all checks..."
	make lint
	make test
	make format

build: ## Build package
	python -m build

install-local: ## Install package locally
	pip install -e .

uninstall: ## Uninstall package
	pip uninstall codecompass -y
