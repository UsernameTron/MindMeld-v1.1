# MindMeld Test Coverage

This document describes how to use the test coverage tools for the MindMeld project.

## Overview

MindMeld uses the following tools for test coverage:

- **Frontend**: Vitest with v8 coverage provider
- **Backend**: pytest with pytest-cov
- **CI Integration**: GitHub Actions with Codecov
- **Reporting**: Coverage badges in README.md

## Running Test Coverage

### Test Environment Setup

Before running tests, you can configure the test environment:

```bash
# Configure the test environment
./scripts/test-setup/configure-test-env.sh
```

This script:
1. Sets up necessary environment variables (MINDMELD_ENV, VECTOR_STORAGE_PATH, etc.)
2. Configures a mock LLM service for testing
3. Creates test data directories and fixture files
4. Sets up a test SQLite database with sample data
5. Creates mock API responses for testing

#### Advanced Testing Options

For more advanced testing scenarios, we provide specialized scripts:

```bash
# Run tests with a mock LLM server
./run_tests_with_mock.sh
```

This starts a Python-based mock LLM server that responds to API requests with predefined responses, allowing you to test the application without connecting to external LLM APIs.

### Using the Coverage Script

The simplest way to run test coverage is to use the provided script:

```bash
# Run tests with coverage only
./run_test_coverage.sh

# Or run with test environment configuration
./run_tests_with_env.sh
```

This will:
1. Configure the test environment (when using run_tests_with_env.sh)
2. Run frontend tests with coverage using Vitest
3. Run backend tests with coverage using pytest-cov
4. Generate HTML and JSON reports in the `coverage` directory

### Running Coverage Separately

#### Frontend Coverage

```bash
cd frontend
npm run test:coverage
```

The coverage report will be available in `coverage/frontend/index.html`.

#### Backend Coverage

```bash
python -m pytest tests/ --cov=src --cov-report=term --cov-report=html:coverage/backend
```

The coverage report will be available in `coverage/backend/index.html`.

### Using the Makefile

A Makefile is also provided for convenience:

```bash
# Run all coverage
make -f Makefile.coverage coverage

# Run only frontend coverage
make -f Makefile.coverage coverage-frontend

# Run only backend coverage
make -f Makefile.coverage coverage-backend

# Clean coverage reports
make -f Makefile.coverage clean
```

## Continuous Integration

Test coverage is automatically run on GitHub Actions for:
- Pull requests to main branch
- Pushes to main branch

The workflow can also be run manually from the GitHub Actions tab.

## Configuration Files

- Frontend:
  - Vitest coverage config in `vitest.config.js`
  - Jest coverage config in `frontend/jest.config.js`

- Backend:
  - pytest-cov config in `.coveragerc`

## Writing Testable Code

### Frontend Testing Guidelines

1. Use data-testid attributes for components that need to be tested:
   ```jsx
   <button data-testid="submit-button">Submit</button>
   ```

2. Use React Testing Library's best practices:
   ```javascript
   import { render, screen } from '@testing-library/react';
   // Prefer user-centric queries
   expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();
   ```

3. Keep components simple and focused on a single responsibility

### Backend Testing Guidelines

1. Use dependency injection to make code easier to test

2. Keep functions small and focused on a single responsibility

3. Use pytest fixtures for common setup

## Viewing Coverage Reports

After running the coverage script, you can view the reports in your browser:

- Frontend: `file://{project_root}/coverage/frontend/index.html`
- Backend: `file://{project_root}/coverage/backend/index.html`

## CI/CD Pipeline Integration

The MindMeld project uses GitHub Actions for its CI/CD pipeline, with comprehensive test coverage reporting.

### GitHub Actions Workflows

1. **Main Branch Validation** (`main-branch-test.yml`):
   - Runs on pushes to main branch, pull requests, and manual triggers
   - Includes jobs for testing, linting, and security checks
   - Uploads coverage reports as artifacts and to Codecov
   - Uses modern GitHub Actions with caching for faster builds

2. **Test Coverage Report** (`test-coverage.yml`):
   - Specialized workflow focused on detailed coverage reports
   - Separate jobs for frontend and backend coverage
   - Generates summarized coverage reports

### Codecov Integration

The project is integrated with [Codecov](https://codecov.io/) for coverage visualization and monitoring:

1. **Configuration**: See `codecov.yml` for settings
2. **Thresholds**:
   - Backend: 80% coverage target
   - Frontend: 70% coverage target
   - Combined: 75% coverage target

3. **PR Checks**: Codecov bot comments on PRs with coverage changes

4. **Badges**: README.md displays automatically updated coverage badges

### Security Checks

The CI pipeline includes multiple security checks:

1. **Python Dependency Checks**:
   - Safety
   - pip-audit
   - Bandit for static analysis

2. **JavaScript Dependency Checks**:
   - npm audit
   - OWASP Dependency Check

3. **Reports**: Security scan results are uploaded as artifacts
