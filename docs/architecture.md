# MindMeld Architecture: Utilities and Agent Structure

## Core Utilities

### File Operations (`utils/file_operations.py`)

The file operations utility provides a standardized way to interact with files in the codebase, with the following benefits:

- **Context Management**: All file operations are properly wrapped in context managers to ensure resources are released.
- **Error Handling**: Consistent error handling with specialized exceptions.
- **Path Normalization**: Automatic conversion between string paths and Path objects.
- **Performance Optimization**: Support for parallel file processing and caching.
- **Filtering Capabilities**: Utilities for filtering files by size, extension, and content.

Key functions:
- `read_file()`: Safely read a file with proper encoding and error handling
- `write_file()`: Safely write to a file with directory creation if needed
- `path_exists()`: Check if a path exists with error handling
- `process_files_parallel()`: Process multiple files in parallel
- `should_process_file()`: Filter files based on size and extension

### Error Handling (`utils/error_handling.py`)

The error handling system provides a hierarchical exception structure to standardize error reporting:

- **Base Exception**: `MindMeldError` serves as the base class for all custom exceptions
- **Specialized Exceptions**: Specific exception types for different error categories
- **Structured Reporting**: Consistent format for error reports in JSON
- **Logging Integration**: Automatic logging of exceptions

Exception hierarchy:
- `MindMeldError`: Base exception class
  - `ValidationError`: Input validation errors
  - `FileProcessingError`: File operation errors
  - `LLMCallError`: LLM interaction errors
    - `ModelUnavailableError`: Missing model errors
    - `TokenLimitError`: Token limit exceeded
    - `ModelTimeoutError`: Model response timeout

### LLM Client (`utils/llm_client.py`)

The LLM client utility provides a robust interface for interacting with language models:

- **Retry Logic**: Automatic retries with exponential backoff using tenacity
- **Model Fallbacks**: Graceful degradation to alternative models
- **Environment Configuration**: Dynamic configuration from environment variables
- **Caching**: Response caching for repeated queries
- **Standardized Interface**: Consistent API across different model providers

Key features:
- Multiple model support (Ollama, OpenAI, etc.)
- Response formatting and validation
- Error handling with specific exception types
- Performance metrics collection

## Agent Structure

### Agent Factory (`packages/agents/AgentFactory.py`)

The Agent Factory provides a central registry for all agents in the system:

- **Dynamic Registration**: Agents can be dynamically registered
- **Input Type Validation**: Defined input types for each agent
- **Creator Functions**: Factory methods to instantiate agents

### Agent Base Class (`packages/agents/advanced_reasoning/agents.py`)

The Agent base class defines the common interface and functionality for all agents:

- **Standard Interface**: Common methods across all agents
- **Error Handling**: Consistent error handling and reporting
- **Metrics Collection**: Performance and usage metrics
- **Resource Management**: Proper resource allocation and cleanup

## Execution Flow

1. **Input Validation**: The `run_agent.py` script validates inputs against the expected types
2. **Agent Creation**: The appropriate agent is instantiated through the factory
3. **Execution**: The agent processes the input and generates a result
4. **Result Normalization**: The result is normalized to comply with the schema
5. **Validation**: The normalized result is validated against the schema
6. **Reporting**: The result is saved to a report file

## Report Structure

All agent reports follow a standardized schema:

```json
{
  "agent": "agent_name",
  "status": "success|error",
  "data": { ... },  // For successful execution
  "error": {         // For error cases
    "message": "Error message",
    "type": "ErrorType"
  },
  "metadata": {
    "agent": "agent_name",
    "timestamp": 1621234567,
    "runtime_seconds": 0.123,
    "system_info": { ... },
    "model_info": { ... }
  }
}
```

## CI/CD Integration

The GitHub Actions workflow (`code-quality.yml`) integrates the agents into the CI/CD pipeline:

- **Matrix Testing**: Parallel execution of different agents
- **Schema Validation**: Validation of agent reports against the schema
- **Docstring Coverage**: Enforcement of documentation standards
- **Report Analysis**: Aggregation and analysis of agent reports

## Future Improvements

- **Agent Orchestration**: More sophisticated agent coordination
- **Distributed Execution**: Support for distributed agent execution
- **Streaming Responses**: Real-time streaming of agent outputs
- **Plugin System**: Extensible plugin architecture for agents
