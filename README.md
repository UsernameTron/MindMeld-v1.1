# MindMeld v1.1

MindMeld is an advanced agent orchestration system powered by local LLMs through Ollama.

## Enhancements

### v1.1 Features

- **Robust LLM Call Handling**:
  - Configurable retries with exponential backoff
  - Timeout controls for reliable operation
  - Fallback model support when primary model fails

- **Improved Error Handling**:
  - Graceful handling of Ollama connection issues
  - Detailed error reporting and status tracking
  - Consistent error structure across all agent types

- **Docker Integration**:
  - Complete containerization of the agent system
  - Multi-container setup with Ollama integration
  - Volume mounts for persistent data

- **API Service**:
  - REST API for agent interaction
  - Synchronous and asynchronous operation modes
  - Comprehensive health checks and monitoring

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/get-started) and Docker Compose
- [Ollama](https://ollama.ai/) (automatically included in Docker setup)

### Running with Docker

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mindmeld-v1.1.git
   cd mindmeld-v1.1
   ```

2. Start the containers:
   ```bash
   docker-compose up -d
   ```

   This will start:
   - Ollama service with GPU acceleration (if available)
   - MindMeld agent system
   - MindMeld API service

3. Access the API at http://localhost:8000

### Environment Variables

Configure the system using these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_HOST` | URL of the Ollama API service | http://localhost:11434 |
| `MAX_RETRIES` | Maximum retry attempts for LLM calls | 3 |
| `BASE_TIMEOUT` | Timeout in seconds for LLM calls | 30 |
| `FALLBACK_MODEL` | Model to use when primary model fails | llama2 |
| `API_PORT` | Port for the API service | 8000 |

## Using the Agents

### Direct Execution

Run an individual agent:

```bash
python run_agent.py <agent_name> "<your-prompt>"
```

Example:
```bash
python run_agent.py ceo "Create a business strategy for an AI startup"
```

### Run All Agents

Execute all agents in sequence:

```bash
python run_all_agents.py
```

### Using the API

The system provides a REST API for agent interaction. See the [API Documentation](docs/api.md) for details.

Basic usage:

```bash
# Get list of available agents
curl http://localhost:8000/agents

# Run an agent synchronously
curl -X POST http://localhost:8000/agents/run \
  -H "Content-Type: application/json" \
  -d '{"agent_name": "ceo", "prompt": "Create a business plan"}'

# Run an agent asynchronously
curl -X POST http://localhost:8000/agents/async-run \
  -H "Content-Type: application/json" \
  -d '{"agent_name": "ceo", "prompt": "Create a business plan"}'

# Check job status
curl http://localhost:8000/jobs/job_1234567890
```

## Development

### Setup Development Environment

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run tests:
   ```bash
   pytest tests/
   ```

### Project Structure

- `packages/agents/` - Agent implementations
- `api.py` - API service implementation
- `scripts/` - Utility scripts
- `tests/` - Test suite
- `docker-compose.yml` - Container orchestration
- `Dockerfile` - Container definition

## Testing

MindMeld includes a comprehensive test suite to ensure reliability and proper functioning of all components. The test suite uses pytest and covers:

- Core agent functionality
- LLM client interaction
- Caching mechanisms
- Knowledge storage
- Workflow orchestration

To run the tests:

```bash
# Run all tests
python -m pytest

# Run specific test module
python -m pytest tests/ai/test_cache.py

# Run with verbose output
python -m pytest -v
```

See `tests/README.md` for detailed information about the test structure.

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for a high-level overview of agent orchestration and reporting.

> The architecture diagram is uploaded as a CI artifact for traceability.

## License

See the [LICENSE](LICENSE) file for details.

## Code Quality

MindMeld maintains high code quality through automated linting and formatting tools.

### Linting

We use Flake8 with several plugins to enforce coding standards:

```bash
# Run linter on the entire codebase
./lint.sh

# Run linter on a specific directory
./lint.sh utils/

# Automatically fix common issues
./lint_fix.sh
```

### Code Style

The project follows these standards:
- [PEP 8](https://www.python.org/dev/peps/pep-0008/) - Python style guide
- Black formatting with line length of 100
- Docstrings using Google style

### Pre-commit Hooks

We use pre-commit hooks to ensure code quality before each commit:

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually on all files
pre-commit run --all-files
```

### CI/CD

The CI pipeline automatically checks code quality on every pull request and push.
See `.github/workflows/code-quality.yml` for details.
