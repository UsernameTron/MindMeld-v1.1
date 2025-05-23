#!/bin/bash

# Set up formatting
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
  echo -e "\n${BOLD}${GREEN}=== $1 ===${NC}\n"
}

print_subheader() {
  echo -e "\n${BOLD}${YELLOW}>> $1${NC}\n"
}

print_error() {
  echo -e "\n${BOLD}${RED}ERROR: $1${NC}\n"
}

print_step() {
  echo -e "${BLUE}• $1${NC}"
}

# Starting message
print_header "MindMeld Test Coverage Runner"
echo -e "Date: $(date)\n"

# Create coverage directories if they don't exist
print_step "Setting up coverage directories"
mkdir -p coverage/frontend
mkdir -p coverage/backend

# Initialize error tracking
FRONTEND_SUCCESS=true
BACKEND_SUCCESS=true

# ===== FRONTEND COVERAGE =====
print_header "Running Frontend Test Coverage (Vitest)"

print_subheader "Installing any missing dependencies"
npm install --no-save @vitest/coverage-v8 || { print_error "Failed to install Vitest coverage dependencies"; FRONTEND_SUCCESS=false; }

if $FRONTEND_SUCCESS; then
  print_subheader "Running Vitest with coverage"
  cd /Users/cpconnor/projects/mindmeld-v1.1
  print_step "Running component tests with coverage"
  npx vitest run --coverage

  # Store the exit code
  FRONTEND_EXIT_CODE=$?

  if [ $FRONTEND_EXIT_CODE -ne 0 ]; then
    print_error "Frontend tests failed with exit code $FRONTEND_EXIT_CODE"
    print_step "Proceeding with other tests despite failure"
    FRONTEND_SUCCESS=false
  fi
fi

# ===== BACKEND COVERAGE =====
print_header "Running Backend Test Coverage (pytest)"

# Check if pytest and coverage are installed
if ! python -c "import pytest, pytest_cov" 2>/dev/null; then
  print_subheader "Installing pytest-cov"
  pip install pytest pytest-cov || { print_error "Failed to install pytest-cov"; BACKEND_SUCCESS=false; }
fi

if $BACKEND_SUCCESS; then
  print_subheader "Running pytest with coverage"
  print_step "Running tests with coverage reporting"
  python -m pytest tests/ \
    --cov=src \
    --cov-config=.coveragerc \
    --cov-report=term \
    --cov-report=html:coverage/backend \
    --cov-report=json:coverage/backend/coverage.json

  # Store the exit code
  BACKEND_EXIT_CODE=$?

  if [ $BACKEND_EXIT_CODE -ne 0 ]; then
    print_error "Backend tests failed with exit code $BACKEND_EXIT_CODE"
    BACKEND_SUCCESS=false
  fi
fi

# ===== SUMMARY =====
print_header "Test Coverage Summary"

# Check if coverage reports exist
FRONTEND_REPORT="coverage/frontend/index.html"
BACKEND_REPORT="coverage/backend/index.html"

if [ -f "$FRONTEND_REPORT" ]; then
  echo -e "${YELLOW}Frontend coverage report:${NC} file://$(pwd)/$FRONTEND_REPORT"

  # Try to extract coverage percentage if available
  if [ -f "coverage/frontend/coverage-summary.json" ]; then
    FRONTEND_COV=$(cat coverage/frontend/coverage-summary.json | grep -o '"pct":[0-9.]*' | head -1 | grep -o '[0-9.]*')
    [ ! -z "$FRONTEND_COV" ] && echo -e "Frontend coverage: ${BOLD}${FRONTEND_COV}%${NC}"
  fi
else
  echo -e "${RED}Frontend coverage report not generated${NC}"
fi

if [ -f "$BACKEND_REPORT" ]; then
  echo -e "${YELLOW}Backend coverage report:${NC} file://$(pwd)/$BACKEND_REPORT"

  # Try to extract coverage percentage if available
  if [ -f "coverage/backend/coverage.json" ]; then
    BACKEND_COV=$(python -c "import json; print(json.load(open('coverage/backend/coverage.json'))['totals']['percent_covered'])" 2>/dev/null)
    [ ! -z "$BACKEND_COV" ] && echo -e "Backend coverage: ${BOLD}${BACKEND_COV}%${NC}"
  fi
else
  echo -e "${RED}Backend coverage report not generated${NC}"
fi

# Generate coverage badges for README
print_subheader "Generating Coverage Badges"
if [ -f "coverage/backend/coverage.json" ] || [ -f "coverage/frontend/coverage-summary.json" ]; then
  print_step "Updating README.md with coverage badges"
  python scripts/generate_coverage_badges.py
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}Coverage badges updated successfully${NC}"
  else
    echo -e "${YELLOW}Failed to update coverage badges${NC}"
  fi
else
  echo -e "${YELLOW}No coverage reports found for badge generation${NC}"
fi

# Status summary
echo
if $FRONTEND_SUCCESS && $BACKEND_SUCCESS; then
  echo -e "${GREEN}${BOLD}Test coverage generation completed successfully!${NC}"
  exit 0
else
  echo -e "${RED}${BOLD}Test coverage generation completed with errors!${NC}"
  exit 1
fi
