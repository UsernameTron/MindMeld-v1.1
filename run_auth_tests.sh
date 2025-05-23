#!/bin/bash

# Run authentication tests and generate coverage report

# Set the environment variable for test coverage
export NODE_ENV=test

# Create coverage directory if it doesn't exist
mkdir -p coverage

# Run Jest tests with coverage for authentication components and APIs
echo "Running authentication tests with coverage..."
cd frontend && npx jest --coverage --coverageReporters=lcov --testPathPattern="__tests__/(api|components)/(token|loginAttempt|resetPassword|forgot-password|reset-password)"

# Run E2E tests for authentication flow
echo "Running E2E authentication tests..."
cd .. && npx playwright test e2e/playwright/tests/auth/login.spec.ts

# Upload coverage to Codecov with auth flag
echo "Uploading coverage reports to Codecov..."
npx codecov -F auth

echo "Authentication test coverage complete!"
