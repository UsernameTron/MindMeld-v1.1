#!/bin/bash

# Script to run Playwright E2E tests
# Usage: ./run-e2e-tests.sh [test-pattern]

set -e

# Install dependencies if needed
if [ ! -d "node_modules/@axe-core" ]; then
  echo "Installing axe-core accessibility testing library..."
  npm install --save-dev @axe-core/playwright
fi

# Set up environment
export NODE_ENV=test

# Run tests with pattern or all tests
if [ -n "$1" ]; then
  echo "Running tests matching pattern: $1"
  npx playwright test "$1"
else
  echo "Running all E2E tests..."
  npx playwright test
fi

# Show the HTML report automatically
echo "Opening HTML report..."
npx playwright show-report