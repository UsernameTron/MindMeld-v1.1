# MindMeld Backend Utilities

This directory contains utility modules designed to improve the stability and reliability of the MindMeld agent system.

## Core Modules

### Model Manager (`model_manager.py`)

The model manager handles LLM dependencies and model availability checking for agent execution.

**Key Features:**
- Model availability checking with configurable retries
- Automatic model pulling capability
- Agent-to-model registry for dependency tracking
- Multiple retry mechanisms for model operations
- Status reporting functions

**Example Usage:**
```python
from utils.model_manager import ModelManager

# Initialize the manager
model_manager = ModelManager()

# Check if a model is available
if model_manager.check_model_availability("phi3.5:latest"):
    print("Model is available!")

# Get the model for a specific agent
agent_model = model_manager.get_agent_model("ceo")

# Try to ensure a model is available (with download if needed)
model_manager.ensure_model_available("llama2:13b")
```

### Error Handling (`error_handling.py`)

Extended error handling with transaction support and retry mechanisms.

**Key Features:**
- Transaction class for atomic operations with rollback
- Retry decorators with configurable backoff
- Enhanced error classes for different failure modes
- Environment detection for production vs. development

**Example Usage:**
```python
from utils.error_handling import Transaction, retry_on_llm_error

# Use a transaction for atomic operations
with Transaction(name="my_operation") as transaction:
    # Register changes that should be rolled back on failure
    transaction.register(lambda: cleanup_temp_files())

    # Execute your code
    # ...

    # Mark transaction as successful
    transaction.register_success()

# Add retry capability to a function
@retry_on_llm_error(max_retries=3, delay=1.0, backoff_factor=2.0)
def call_llm_with_retries():
    # This will automatically retry on LLM errors
    return llm_client.generate(prompt)
```

### Schema Validator (`schema_validator.py`)

Provides consistent schema validation for agent inputs and outputs.

**Key Features:**
- JSON schema loading and validation
- Agent output normalization
- Input type validation for different agents
- Standard error formatting
- Report fixing capabilities

**Example Usage:**
```python
from utils.schema_validator import validate_agent_output, normalize_agent_output

# Normalize an agent output
normalized = normalize_agent_output(
    output=raw_result,
    agent_name="ceo",
    payload="example/path",
    timestamp=int(time.time()),
    runtime_seconds=2.5,
    job_id="job_123"
)

# Validate against schema
is_valid, error = validate_agent_output(normalized)
if not is_valid:
    print(f"Validation error: {error}")
```

### Testing Utilities (`testing_utils.py`)

Comprehensive testing support for agents and their dependencies.

**Key Features:**
- Mock LLM response generation
- Mock Ollama client
- Testing utilities for creating test files and directories
- Schema validation assertions
- Agent testing base class

**Example Usage:**
```python
from utils.testing_utils import MockOllamaClient, AgentTestCase

# Create a mock client for testing
mock_client = MockOllamaClient(responses={
    "Hello": "Hello, how can I help you?",
    "Tell me about": "I can provide information about that topic."
})

# Use the agent test case base class
class MyAgentTest(AgentTestCase):
    def test_agent_execution(self):
        # This will use mocks instead of real LLM calls
        with self.patch_llm_calls():
            result = self.agent.run("test input")
            self.assert_agent_report_format(result)
```

## Integration Example

See `integration_example.py` for a complete example of how to use these utilities together in your agent implementations.

## Best Practices

1. **Model Management**: Always use `ModelManager` to check for model availability before executing agents.

2. **Error Handling**: Wrap critical operations in `Transaction` contexts and use retry decorators for operations prone to transient failures.

3. **Validation**: Validate all agent outputs with `schema_validator` functions to ensure consistent reporting format.

4. **File Operations**: Use `safe_file_write` rather than direct file operations to prevent data corruption.

5. **Testing**: Utilize the testing utilities to write comprehensive tests without requiring actual LLM calls.
