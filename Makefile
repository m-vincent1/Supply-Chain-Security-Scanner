.PHONY: install test lint run-api run-frontend docker-up docker-down clean help

PYTHON := python3
BACKEND_DIR := backend
CLI_DIR := cli

help:
	@echo "Supply Chain Security Scanner — available commands:"
	@echo ""
	@echo "  make install        Install all dependencies (backend + CLI)"
	@echo "  make test           Run all tests"
	@echo "  make lint           Run linter"
	@echo "  make run-api        Start the FastAPI backend (dev mode)"
	@echo "  make run-frontend   Start the React frontend (dev mode)"
	@echo "  make docker-up      Start all services with Docker Compose"
	@echo "  make docker-down    Stop Docker Compose services"
	@echo "  make clean          Remove generated files"
	@echo "  make demo           Run a demo scan on sample projects"

install:
	cd $(BACKEND_DIR) && pip install -e ".[dev]"
	cd $(CLI_DIR) && pip install -e ".[dev]"
	cd frontend && npm install

test:
	cd $(BACKEND_DIR) && python -m pytest tests/ -v

lint:
	cd $(BACKEND_DIR) && python -m ruff check app/ tests/ || true
	cd $(CLI_DIR) && python -m ruff check scs_scanner/ tests/ || true

run-api:
	cd $(BACKEND_DIR) && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	cd frontend && npm run dev

docker-up:
	docker compose up --build -d
	@echo ""
	@echo "Services started:"
	@echo "  Frontend:  http://localhost:5173"
	@echo "  Backend:   http://localhost:8000"
	@echo "  API docs:  http://localhost:8000/docs"

docker-down:
	docker compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -f backend/data/scans.db

demo:
	@echo "Running demo scans..."
	cd $(CLI_DIR) && python -m scs_scanner.main scan ../sample-projects/python-vulnerable --format markdown --output ../reports/python-vulnerable.md --verbose
	cd $(CLI_DIR) && python -m scs_scanner.main scan ../sample-projects/python-secure --format markdown --output ../reports/python-secure.md
	cd $(CLI_DIR) && python -m scs_scanner.main scan ../sample-projects/node-vulnerable --format json --output ../reports/node-vulnerable.json
	cd $(CLI_DIR) && python -m scs_scanner.main scan ../sample-projects/java-vulnerable --format html --output ../reports/java-vulnerable.html
	@echo ""
	@echo "Reports generated in reports/"
