# MindMeld Agent API Documentation

MindMeld Agent API provides REST endpoints for interacting with the MindMeld agent system. This API allows you to run agents, check their status, and retrieve results asynchronously.

## Base URL

- Local development: `http://localhost:8000`
- Docker: `http://localhost:8000`

## Authentication

*Note: Authentication is not implemented in the current version. This would be added in a future update.*

## Endpoints

### Health Check

**Endpoint:** `GET /health`

**Description:** Check the health status of the API and its dependencies.

**Response:**
```json
{
  "status": "healthy",
  "ollama_status": true,
  "version": "1.1.0"
}
```

- `status`: Overall status of the API ("healthy" or "degraded")
- `ollama_status`: Whether Ollama is available
- `version`: Current API version

### List Agents

**Endpoint:** `GET /agents`

**Description:** List all available agents in the system.

**Response:**
```json
{
  "agents": ["ceo", "planner", "executor", "programmer", "image_analyzer"],
  "total": 5
}
```

### Run Agent (Synchronous)

**Endpoint:** `POST /agents/run`

**Description:** Run an agent with the provided prompt and wait for the result.

**Request Body:**
```json
{
  "agent_name": "ceo",
  "prompt": "Create a business plan for a tech startup",
  "max_retries": 3,
  "timeout": 60
}
```

- `agent_name`: (Required) Name of the agent to run
- `prompt`: (Required) The input to send to the agent
- `max_retries`: (Optional) Maximum number of retries if the agent fails
- `timeout`: (Optional) Timeout in seconds for each attempt

**Response:**
```json
{
  "agent": "ceo",
  "result": "Here's a business plan outline for your tech startup...",
  "execution_time": 12.34,
  "status": "success"
}
```

**Error Response:**
```json
{
  "agent": "ceo",
  "result": {
    "error": "ceo failed after 3 attempts",
    "details": "Check if Ollama is running and the model is available."
  },
  "execution_time": 45.67,
  "status": "error"
}
```

### Run Agent (Asynchronous)

**Endpoint:** `POST /agents/async-run`

**Description:** Run an agent asynchronously and return a job ID.

**Request Body:**
```json
{
  "agent_name": "ceo",
  "prompt": "Create a business plan for a tech startup",
  "max_retries": 3,
  "timeout": 60
}
```

**Response:**
```json
{
  "job_id": "job_1701234567",
  "status": "submitted"
}
```

### Get Job Status

**Endpoint:** `GET /jobs/{job_id}`

**Description:** Get the status and result of an asynchronous job.

**Response (Success):**
```json
{
  "job_id": "job_1701234567",
  "agent": "ceo",
  "prompt": "Create a business plan for a tech startup",
  "result": "Here's a business plan outline for your tech startup...",
  "execution_time": 12.34,
  "status": "success",
  "completed_at": 1701234590.123
}
```

**Response (Error):**
```json
{
  "job_id": "job_1701234567",
  "agent": "ceo",
  "prompt": "Create a business plan for a tech startup",
  "error": "Error message",
  "status": "error",
  "completed_at": 1701234590.123
}
```

## Error Codes

- `404` - Resource not found (agent or job)
- `503` - Service unavailable (Ollama not available)
- `500` - Internal server error

## Examples

### Example: Running a CEO Agent

```bash
curl -X POST http://localhost:8000/agents/run \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "ceo",
    "prompt": "Create a business plan for a tech startup"
  }'
```

### Example: Running an Async Job

```bash
curl -X POST http://localhost:8000/agents/async-run \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "ceo",
    "prompt": "Create a business plan for a tech startup"
  }'
```

### Example: Checking Job Status

```bash
curl -X GET http://localhost:8000/jobs/job_1701234567
```
