.PHONY: dev install clean format lint help setup-search render-build render-start
# Default target
.DEFAULT_GOAL := help

# Variables
PORT = 8000

help:
	@echo "Available commands:"
	@echo "  make install             - Install dependencies using uv"
	@echo "  make dev                 - Run development server with reload"
	@echo "  make start               - Run production server"
	@echo "  make render-build        - Build for Render deployment"
	@echo "  make render-start        - Start for Render deployment"
	@echo "  make clean               - Remove Python cache files"
	@echo "  make format              - Format code using black"
	@echo "  make lint                - Run linting using ruff"
	@echo "  make setup-search        - Setup product search indexes"

install:
	uv pip install -e ".[dev]"

# Render-specific build (no venv needed on Render)
render-build:
	pip install uv
	uv pip install --system uvicorn
	uv pip install --system -e ".[dev]"

# Render-specific start
render-start:
	uvicorn main:app --host 0.0.0.0 --port $${PORT:-8000}

dev:
	uv pip install uvicorn
	uv run uvicorn main:app --reload --port $(PORT)

start:
	uv run uvicorn main:app --port $(PORT)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".ruff_cache" -exec rm -rf {} +
	find . -type f -name ".pytest_cache" -exec rm -rf {} +

format:
	uv run black .

lint:
	uv run ruff check .

setup-vscode:
	code --install-extension ms-python.python
	code --install-extension ms-python.black-formatter
	code --install-extension charliermarsh.ruff

setup-search:
	@echo "🚀 Setting up Product Search Pipeline..."
	uv run python scripts/setup_product_search.py