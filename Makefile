# Employee Directory API - Makefile
# Professional development workflow

.PHONY: help install setup dev test lint clean docker-build docker-run docs

# Default target
help:
	@echo "🚀 Employee Directory API - Development Commands"
	@echo "=================================================="
	@echo ""
	@echo "📦 Setup Commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make setup       - Full project setup (install + db)"
	@echo ""
	@echo "🔧 Database Commands:"
	@echo "  make init-db     - Initialize basic database"
	@echo "  make init-oauth2 - Setup OAuth2 tables"
	@echo "  make init-async  - Initialize async database"
	@echo ""
	@echo "🚀 Development Commands:"
	@echo "  make dev         - Start development server"
	@echo "  make test        - Run tests with coverage"
	@echo "  make lint        - Run code linting"
	@echo ""
	@echo "🔐 Authentication Commands:"
	@echo "  make tokens      - Generate JWT tokens"
	@echo ""
	@echo "🐳 Docker Commands:"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run with Docker Compose"
	@echo ""
	@echo "🧹 Maintenance Commands:"
	@echo "  make clean       - Clean temporary files"
	@echo "  make docs        - Open API documentation"

# Setup commands
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

setup: install init-db init-oauth2 tokens
	@echo "✅ Project setup complete!"

# Database commands
init-db:
	@echo "🗄️ Initializing database..."
	python scripts/create_tables.py

init-oauth2:
	@echo "🔐 Setting up OAuth2 tables..."
	python scripts/create_oauth2_tables.py

init-async:
	@echo "⚡ Initializing async database..."
	python scripts/init_async_db.py

# Development commands
dev:
	@echo "🚀 Starting development server..."
	python main.py

test:
	@echo "🧪 Running tests with coverage..."
	python scripts/run_tests.py

lint:
	@echo "🔍 Running code linting..."
	@if command -v black >/dev/null 2>&1; then \
		black --check app/ scripts/ tests/; \
	else \
		echo "⚠️ black not installed. Install with: pip install black"; \
	fi
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 app/ scripts/ tests/; \
	else \
		echo "⚠️ flake8 not installed. Install with: pip install flake8"; \
	fi

# Authentication commands
tokens:
	@echo "🔑 Generating JWT tokens..."
	python scripts/generate_jwt_token.py

# Docker commands
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t employee-directory-api .

docker-run:
	@echo "🐳 Starting with Docker Compose..."
	docker-compose up -d

# Maintenance commands
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf coverage_reports/ 2>/dev/null || true
	rm -f .coverage 2>/dev/null || true

docs:
	@echo "📖 Opening API documentation..."
	@echo "🌐 Swagger UI: http://localhost:8000/docs"
	@echo "📚 ReDoc: http://localhost:8000/redoc"
	@if command -v open >/dev/null 2>&1; then \
		open http://localhost:8000/docs; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open http://localhost:8000/docs; \
	fi

# Production commands
prod:
	@echo "🏭 Starting production server..."
	uvicorn main:app --host 0.0.0.0 --port 8000

# Quick demo setup
demo: setup
	@echo "🎬 Setting up demo environment..."
	python scripts/init_async_db.py
	@echo ""
	@echo "✅ Demo ready! Run 'make dev' to start server"
	@echo "📖 Visit http://localhost:8000/docs for API documentation" 