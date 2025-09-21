.PHONY: dev install clean format lint help
# Default target
.DEFAULT_GOAL := help

# Variables
PORT = 8000

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies using uv"
	@echo "  make dev       - Run development server with reload"
	@echo "  make start     - Run production server"
	@echo "  make clean     - Remove Python cache files"
	@echo "  make format    - Format code using black"
	@echo "  make lint      - Run linting using ruff"

install:
	uv pip install -e ".[dev]"

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
