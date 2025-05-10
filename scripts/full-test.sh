#!/usr/bin/env bash
set -euo pipefail

# Use the correct project root path
cd "$(dirname "$0")/.."

# Define phases that can be run independently
run_backend_tests() {
  echo "🛠 Phase 0: Backend Tests"
  pytest --maxfail=1 --disable-warnings -q
}

run_frontend_lint() {
  echo "🛠 Phase 1: Frontend Lint/Format/Type Checks"
  cd frontend
  npm run lint
  npm run format:check
  npm run type-check
  cd ..
}

run_frontend_tests() {
  echo "🛠 Phase 2: Frontend Unit Tests"
  cd frontend
  npm run test:coverage
  cd ..
}

run_frontend_build() {
  echo "🛠 Phase 3: Production Build"
  cd frontend
  npm run build
  cd ..
}

run_e2e_tests() {
  echo "🛠 Phase 4: Playwright E2E Tests"
  cd frontend
  # ensure the app is built or dev‐server is available
  # CI will set NODE_ENV=production so secure cookies get enforced
  NODE_ENV=production npx playwright test --config=../playwright.config.ts
  cd ..
}

# Default: run all phases
if [[ $# -eq 0 ]]; then
  run_backend_tests
  run_frontend_lint
  run_frontend_tests
  run_frontend_build
  run_e2e_tests
  echo "✅ All phases 0–4 passed!"
  exit 0
fi

# Run specific phases if provided as arguments
for arg in "$@"; do
  case $arg in
    backend|0)
      run_backend_tests
      ;;
    lint|1)
      run_frontend_lint
      ;;
    unit|2)
      run_frontend_tests
      ;;
    build|3)
      run_frontend_build
      ;;
    e2e|4)
      run_e2e_tests
      ;;
    *)
      echo "Unknown phase: $arg"
      echo "Usage: $0 [backend|lint|unit|build|e2e]"
      exit 1
      ;;
  esac
done

echo "✅ Requested phases completed!"
