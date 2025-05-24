#!/bin/bash
# start_api.sh - Script to start the MindMeld API service

# Check if OLLAMA_HOST is set, otherwise use default
if [ -z "$OLLAMA_HOST" ]; then
    export OLLAMA_HOST=http://localhost:11434
fi

# Check if Ollama is available
echo "Checking if Ollama is available at $OLLAMA_HOST..."
python3 scripts/wait_for_ollama.py --host $OLLAMA_HOST --timeout 60

# Set the API port or use default
if [ -z "$API_PORT" ]; then
    export API_PORT=8000
fi

# Create necessary directories
mkdir -p logs
mkdir -p outputs
mkdir -p outputs/jobs

# Start the API service
echo "Starting MindMeld API on port $API_PORT..."
uvicorn api:app --host 0.0.0.0 --port $API_PORT --log-level info &

# Start the API server
python api.py
