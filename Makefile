install:
	pip install -r requirements.txt

dev-deps:
	pip install -r requirements.txt
	pip install black isort mypy pytest pytest-cov pre-commit uvicorn

dev: dev-deps
	pre-commit install

start:
	uvicorn app.main:app --reload

test:
	pytest --cov=app --cov-report=term-missing

format:
	black .
	isort .

lint:
	black --check .
	isort --check-only .
	flake8 --statistics .

flake8:
	flake8 --statistics --count .

static-analysis:
	black --check .
	isort --check-only .
	flake8 --statistics .
	mypy --strict .
	bandit -r app/ -c pyproject.toml
	safety check || true

# To use in CI, add a step:
#   make static-analysis
# and ensure all required tools are installed.

clean:
	find . -type d -name '__pycache__' -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	find . -type f -name '*.coverage' -delete
	find . -type d -name '.pytest_cache' -exec rm -rf {} +
	find . -type d -name '.mypy_cache' -exec rm -rf {} +

generate_dot_env:
	cp .env.example .env

# --- Frontend (MindMeld) ---
fetch-schema:
	cd frontend && npx ts-node --esm src/api/schema/fetch-schema.ts

generate-types:
	cd frontend && npm run generate-types

storybook:
	cd frontend && npm run storybook

.PHONY: install dev-deps dev start test format lint flake8 static-analysis clean generate_dot_env fetch-schema generate-types storybook run-agent start-api update-tools verify-api

# Updated targets
test-suite:         # run tests with pytest
	pytest tests/

lint-check:         # run lint checks
	flake8 .

run-agent:          # run single agent
	python scripts/agents/run_agent_simple.py --list

start-api:          # start API server
	bash scripts/start_api.sh

update-tools:       # update agent tool definitions
	python scripts/update_agent_tools.py

verify-api:         # verify API tool compatibility
	python scripts/verify_api_tools.py
