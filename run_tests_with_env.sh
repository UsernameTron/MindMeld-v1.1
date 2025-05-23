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

print_step() {
  echo -e "${BLUE}• $1${NC}"
}

# Starting message
print_header "MindMeld Test Environment Setup"
echo -e "Date: $(date)\n"

# Source the environment configuration
print_step "Configuring test environment..."
source ./scripts/test-setup/configure-test-env.sh

# Create the test database if needed
print_step "Setting up test database..."
# Placeholder for database setup (if applicable)
# This would be replaced with actual DB setup commands

# Run the tests with coverage
print_step "Running test coverage with test environment..."
./run_test_coverage.sh

# Exit with success
echo -e "\n${GREEN}Test setup and execution complete!${NC}\n"
exit 0
