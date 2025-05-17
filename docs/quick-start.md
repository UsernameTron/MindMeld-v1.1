# MindMeld v1.1 Quick Start Guide

This guide helps you get started with the enhanced MindMeld v1.1 agent system quickly.

## Installation Options

### Option 1: Docker Setup (Recommended)

The simplest way to use MindMeld is with Docker, which includes everything you need:

1. **Prerequisites**:
   - [Docker](https://www.docker.com/get-started) and Docker Compose
   - No local Ollama installation needed (it's included in containers)

2. **Start the system**:
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/mindmeld-v1.1.git
   cd mindmeld-v1.1
   
   # Start all services
   docker-compose up -d
   ```

3. **Verify it's running**:
   ```bash
   # Check container status
   docker-compose ps
   
   # Check API health
   curl http://localhost:8000/health
   ```

4. **Use the API**:
   ```bash
   # List available agents
   curl http://localhost:8000/agents
   
   # Run an agent
   curl -X POST http://localhost:8000/agents/run \
     -H "Content-Type: application/json" \
     -d '{"agent_name": "ceo", "prompt": "Create a business plan for an AI startup"}'
   ```

### Option 2: Local Installation

If you prefer to run without Docker:

1. **Prerequisites**:
   - Python 3.10+
   - [Ollama](https://ollama.ai/) installed and running locally

2. **Setup**:
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/mindmeld-v1.1.git
   cd mindmeld-v1.1
   
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Start the API service**:
   ```bash
   # Start the API
   python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Start Ollama** (if not already running):
   ```bash
   # In a separate terminal
   ollama serve
   ```

## Running Agents

### Method 1: Using the API (Recommended)

The API provides both synchronous and asynchronous execution modes:

#### Synchronous (wait for result):

```bash
curl -X POST http://localhost:8000/agents/run \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "ceo",
    "prompt": "Create a business plan for an AI startup",
    "max_retries": 3,
    "timeout": 60
  }'
```

#### Asynchronous (get a job ID):

```bash
# Submit job
curl -X POST http://localhost:8000/agents/async-run \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "ceo",
    "prompt": "Create a business plan for an AI startup"
  }'

# Check job status (replace job_id with the ID from the response)
curl http://localhost:8000/jobs/job_1234567890
```

### Method 2: Command Line

You can also run agents directly from the command line:

```bash
# Run a single agent
python run_agent.py ceo "Create a business plan for an AI startup"

# Run all agents
python run_all_agents.py --wait-for-ollama --verify-models
```

## Configuration

### Environment Variables

Customize MindMeld with these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_HOST` | URL of the Ollama API | http://localhost:11434 |
| `MAX_RETRIES` | Max retry attempts | 3 |
| `BASE_TIMEOUT` | Timeout in seconds | 30 |
| `FALLBACK_MODEL` | Fallback model name | llama2 |
| `API_PORT` | API service port | 8000 |

### Setting Environment Variables

#### With Docker:

In `docker-compose.yml`:
```yaml
services:
  mindmeld:
    environment:
      - MAX_RETRIES=5
      - FALLBACK_MODEL=mistral
```

Or when running:
```bash
MAX_RETRIES=5 FALLBACK_MODEL=mistral docker-compose up -d
```

#### Without Docker:

```bash
# Set for current session
export MAX_RETRIES=5
export FALLBACK_MODEL=mistral
python run_agent.py ceo "Create a business plan"

# Or set inline
MAX_RETRIES=5 FALLBACK_MODEL=mistral python run_agent.py ceo "Create a business plan"
```

## Troubleshooting

### Common Issues

1. **Ollama Connection Errors**:
   - Ensure Ollama is running: `curl http://localhost:11434/api/tags`
   - Check Docker container status: `docker ps`
   - Verify environment variables: `echo $OLLAMA_HOST`

2. **Missing Models**:
   - Pull required models: `ollama pull llama2`
   - Use the `--verify-models` flag: `python run_all_agents.py --verify-models`

3. **API Not Responding**:
   - Check if the service is running: `curl http://localhost:8000/health`
   - Check Docker logs: `docker-compose logs api`

### Logs

Check logs for detailed error information:

```bash
# API logs
cat logs/api_*.log

# Agent run logs
cat logs/agent_run_*.log

# Docker logs
docker-compose logs api
docker-compose logs ollama
docker-compose logs mindmeld
```

## Next Steps

- Read the full [API Documentation](api.md)
- Explore the [Agent Guide](../AGENT_GUIDE.md)
- Check the [Implementation Summary](implementation-summary.md)
