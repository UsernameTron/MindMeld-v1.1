# MindMeld v1.1 - Standardized Agent System

## Overview

MindMeld v1.1 is an advanced multi-agent system featuring standardized agent protocols, comprehensive sentiment analysis capabilities, and production-ready infrastructure for AI-powered code analysis, testing, and deployment automation.

## 🚀 Key Features

- **Standardized Agent Protocol**: Unified interface for all agent implementations
- **Advanced Sentiment Analysis**: Multi-framework support with comprehensive API
- **Code Intelligence**: Automated debugging, dependency management, and test generation
- **Vector Memory System**: Optimized semantic search with FAISS integration
- **Production Infrastructure**: Rate limiting, caching, error handling, and monitoring
- **Comprehensive Testing**: End-to-end test suites with detailed reporting

## 📋 Table of Contents

- [Architecture](#architecture)
- [Agent Types](#agent-types)
- [Getting Started](#getting-started)
- [Usage Examples](#usage-examples)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Development](#development)
- [Contributing](#contributing)

## 🏗 Architecture

### Core Components

```
packages/
├── agents/
│   ├── base/                    # Core agent protocols and registry
│   │   ├── protocols.py         # AgentProtocol interface
│   │   └── registry.py          # Centralized agent management
│   ├── implementations/         # Standardized agent implementations
│   │   ├── code_debug.py        # Code debugging and analysis
│   │   ├── critic.py            # Output evaluation and feedback
│   │   ├── executor.py          # Task execution
│   │   ├── planner.py           # Task planning and orchestration
│   │   └── test_generator.py    # Automated test generation
│   └── claude_agents/           # Claude API integration
│       ├── agents/              # Agent implementations
│       ├── api/                 # API clients and optimization
│       └── core/                # Core functionality
```

### Agent Protocol Standard

All agents implement the `AgentProtocol` interface:

```python
class AgentProtocol(Protocol):
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return structured output"""

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input parameters"""

    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities and metadata"""
```

## 🤖 Agent Types

### CodeDebugAgent
Advanced code analysis with multiple check types:
- **Syntax Analysis**: AST parsing and syntax error detection
- **Logic Validation**: Control flow and algorithm analysis
- **Performance Optimization**: Bottleneck identification
- **Security Scanning**: Vulnerability detection and security best practices

```python
from packages.agents.implementations.code_debug import CodeDebugAgent

agent = CodeDebugAgent()
result = agent.process({
    "code": "def example(): print('Hello')",
    "file_path": "example.py"
})
```

### CriticAgent
Output evaluation and quality assessment:
- **Response Quality**: Accuracy and completeness scoring
- **Coherence Analysis**: Logical consistency validation
- **Improvement Suggestions**: Actionable feedback generation

### ExecutorAgent
Task execution with tool integration:
- **Command Execution**: Safe subprocess management
- **Tool Integration**: External tool orchestration
- **Result Validation**: Output verification and error handling

### PlannerAgent
Strategic task breakdown and planning:
- **Goal Decomposition**: Complex task analysis
- **Step Sequencing**: Optimal execution ordering
- **Resource Allocation**: Agent and tool assignment

### TestGeneratorAgent
Automated test suite generation:
- **Framework Support**: pytest, unittest, jest
- **Coverage Analysis**: Code path examination
- **Edge Case Detection**: Boundary condition testing

## 🚀 Getting Started

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd mindmeld-v1.1
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

4. **Initialize the system**:
```bash
python -c "from packages.agents.base.registry import AgentRegistry; print('System ready')"
```

### Prerequisites

```bash
# Python 3.8+
python --version

# Required dependencies
pip install -r requirements.txt
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

## Quick Start

```python
from packages.agents.base.registry import AgentRegistry
from packages.agents.implementations.code_debug import CodeDebugAgent

# Initialize registry
registry = AgentRegistry.get_instance()

# Create and use an agent
debug_agent = CodeDebugAgent()
result = debug_agent.process({
    "code": """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
    """,
    "file_path": "fibonacci.py"
})

print(f"Analysis complete: {result['status']}")
print(f"Issues found: {len(result['data']['issues'])}")
```

## 📖 Usage Examples

### 1. Code Analysis Pipeline

```python
from packages.agents.implementations import (
    CodeDebugAgent,
    TestGeneratorAgent,
    CriticAgent
)

# Create analysis pipeline
debug_agent = CodeDebugAgent()
test_agent = TestGeneratorAgent()
critic_agent = CriticAgent()

# Analyze code
code_analysis = debug_agent.process({
    "code": open("myfile.py").read(),
    "file_path": "myfile.py"
})

# Generate tests
test_results = test_agent.process({
    "code": open("myfile.py").read(),
    "file_path": "myfile.py",
    "test_framework": "pytest"
})

# Evaluate results
evaluation = critic_agent.process({
    "content": test_results["data"]["test_code"],
    "criteria": ["completeness", "correctness", "coverage"]
})
```

### 2. Workflow Orchestration

```python
from packages.agents.base.registry import AgentRegistry

registry = AgentRegistry.get_instance()

# Register agents
registry.register_agent(
    "code_debug",
    lambda **kwargs: CodeDebugAgent(**kwargs),
    {"description": "Code debugging and analysis"}
)

registry.register_agent(
    "test_generator",
    lambda **kwargs: TestGeneratorAgent(**kwargs),
    {"description": "Automated test generation"}
)

# Create workflow
registry.create_workflow("code_analysis", ["code_debug", "test_generator"])

# Execute workflow
result = registry.execute_workflow("code_analysis", {
    "code": "def hello(): print('Hello World')",
    "file_path": "hello.py"
})
```

### 3. Sentiment Analysis API

```python
# Direct API usage
import requests

response = requests.post("http://localhost:8000/analyze", json={
    "content": "This product is amazing! I love the new features.",
    "url": "https://example.com/review"
})

result = response.json()
print(f"Sentiment: {result['sentiment']}")
print(f"Confidence: {result['confidence']}")
```

## 📚 API Documentation

### Core Endpoints

#### `/analyze` - Sentiment Analysis
- **Method**: POST
- **Content-Type**: application/json

**Request Body**:
```json
{
    "content": "Text to analyze (optional if url provided)",
    "url": "URL to fetch content from (optional if content provided)",
    "advanced": true,
    "include_topics": true,
    "include_entities": true
}
```

**Response**:
```json
{
    "sentiment": "positive|negative|neutral",
    "confidence": 0.85,
    "scores": {
        "positive": 0.85,
        "negative": 0.10,
        "neutral": 0.05
    },
    "topics": ["product", "features"],
    "entities": ["product", "features"],
    "processing_time": 0.123
}
```

### Agent Capabilities

Each agent exposes its capabilities through the `get_capabilities()` method:

```python
agent = CodeDebugAgent()
capabilities = agent.get_capabilities()

print(capabilities)
# Output:
{
    "name": "CodeDebugAgent",
    "description": "Advanced code debugging and analysis",
    "version": "1.0.0",
    "supported_languages": ["python"],
    "check_types": ["syntax", "logic", "performance", "security"],
    "required_inputs": ["code"],
    "optional_inputs": ["file_path", "check_types"],
    "output_schema": {
        "status": "success|error",
        "data": {
            "issues": "List[Dict]",
            "suggestions": "List[str]",
            "metrics": "Dict"
        }
    }
}
```

## 🧪 Testing

### Test Structure

```
tests/
├── agents/                      # Agent-specific tests
│   ├── test_agent_implementations.py
│   └── test_registry.py
├── api/                         # API endpoint tests
│   ├── test_sentiment_analysis.py
│   └── test_url_processing.py
└── integration/                 # End-to-end tests
    ├── test_workflow_execution.py
    └── test_agent_pipeline.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/agents/ -v
pytest tests/api/ -v
pytest tests/integration/ -v

# Run with coverage
pytest --cov=packages/ --cov-report=html

# Run integration tests
python test_integration.py
python test_sentiment_api.py
```

### Test Reports

Detailed test reports are generated in `/test_results/`:
- `standardized_agents_test_report.json` - Comprehensive test results
- Individual agent reports in `/reports/` directory

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

## 🛠 Development

### Project Structure

```
mindmeld-v1.1/
├── app/                         # FastAPI application
│   ├── api/routes/             # API route definitions
│   └── models/                 # Request/response models
├── frontend/                   # React frontend
│   └── src/services/          # API service clients
├── packages/agents/           # Agent system
│   ├── base/                  # Core protocols
│   ├── implementations/       # Standard agents
│   └── claude_agents/        # Claude integration
├── scripts/                   # Utility scripts
├── tests/                     # Test suites
└── docs/                      # Documentation
```

### Adding New Agents

1. **Implement the AgentProtocol**:
```python
from packages.agents.base.protocols import AgentProtocol
from packages.agents.base.registry import AgentRegistry

class MyCustomAgent(AgentProtocol):
    def process(self, input_data):
        # Implementation
        return {"status": "success", "data": result}

    def validate_input(self, input_data):
        # Validation logic
        return True

    def get_capabilities(self):
        return {
            "name": "MyCustomAgent",
            "description": "Custom functionality",
            "version": "1.0.0"
        }
```

2. **Register the agent**:
```python
registry = AgentRegistry.get_instance()
registry.register_agent(
    "my_custom_agent",
    lambda **kwargs: MyCustomAgent(**kwargs),
    {"description": "Custom agent implementation"}
)
```

### Environment Configuration

Key environment variables:

```bash
# API Configuration
CLAUDE_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_api_key

# Database
DATABASE_URL=postgresql://user:pass@localhost/mindmeld

# Caching
REDIS_URL=redis://localhost:6379

# Monitoring
ENABLE_MONITORING=true
LOG_LEVEL=INFO
```

## 📈 Monitoring and Analytics

### Built-in Monitoring

The system includes comprehensive monitoring:

```python
from packages.agents.claude_agents.monitoring.dashboard import AgentMonitor

monitor = AgentMonitor()
stats = monitor.get_usage_stats()

print(f"Total requests: {stats['request_count']}")
print(f"Average response time: {stats['avg_response_time']}s")
print(f"Cost tracking: ${stats['total_cost']}")
```

### Performance Metrics

- **Response Times**: Per-agent performance tracking
- **Token Usage**: Claude API consumption monitoring
- **Error Rates**: Failure analysis and alerting
- **Cache Efficiency**: Hit rates and optimization

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-agent`
3. **Implement changes** following the agent protocol
4. **Add tests** for new functionality
5. **Run test suite**: `pytest`
6. **Submit pull request**

### Code Standards

- **Type Hints**: All functions must include type annotations
- **Documentation**: Docstrings for all public methods
- **Testing**: Unit tests for all new agents
- **Linting**: Code must pass flake8 and black formatting

### Agent Development Guidelines

1. **Follow the Protocol**: Implement all required methods
2. **Error Handling**: Graceful failure with informative messages
3. **Input Validation**: Robust validation for all inputs
4. **Output Consistency**: Standardized response format
5. **Performance**: Optimize for production use

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [API Documentation](./docs/api/)
- [Agent Interfaces](./docs/agent_interfaces.md)
- [Architecture Overview](./ARCHITECTURE.md)
- [Testing Guide](./docs/testing.md)

## 📞 Support

For questions and support:
- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Comprehensive guides in `/docs/`
- **Examples**: Sample implementations in `/examples/`

---

**MindMeld v1.1** - Building the future of intelligent agent systems.
