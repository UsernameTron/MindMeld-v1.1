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
print_header "MindMeld Mock LLM Test Environment"
echo -e "Date: $(date)\n"

# Source the environment configuration
print_step "Configuring test environment..."
source ./scripts/test-setup/configure-test-env.sh

# Check if the mock LLM server process is already running
MOCK_SERVER_PID=$(ps aux | grep "[m]ock_llm_server.py" | awk '{print $2}')
if [ ! -z "$MOCK_SERVER_PID" ]; then
  echo -e "${YELLOW}Mock LLM server is already running with PID $MOCK_SERVER_PID${NC}"
  echo -e "${YELLOW}Stopping existing server...${NC}"
  kill $MOCK_SERVER_PID
  sleep 1
fi

# Start the mock LLM server
print_step "Starting mock LLM server on port $MOCK_LLM_PORT..."
python ./scripts/test-setup/mock_llm_server.py --port $MOCK_LLM_PORT &
MOCK_SERVER_PID=$!

# Wait a moment for server to start
sleep 2

# Check if server started successfully
if ps -p $MOCK_SERVER_PID > /dev/null; then
  echo -e "${GREEN}Mock LLM server started with PID $MOCK_SERVER_PID${NC}"

  # Save PID for later cleanup
  echo $MOCK_SERVER_PID > ./test_data/mock_server.pid
else
  echo -e "${RED}Failed to start mock LLM server${NC}"
  exit 1
fi

# Run the tests with coverage
print_step "Running tests with mock LLM server..."
./run_test_coverage.sh

# Cleanup - stop the mock server
if [ -f ./test_data/mock_server.pid ]; then
  MOCK_SERVER_PID=$(cat ./test_data/mock_server.pid)
  print_step "Stopping mock LLM server (PID $MOCK_SERVER_PID)..."
  kill $MOCK_SERVER_PID 2>/dev/null || true
  rm ./test_data/mock_server.pid
fi

# Exit with success
echo -e "\n${GREEN}Tests complete!${NC}\n"
exit 0
