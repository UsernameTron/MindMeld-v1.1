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
