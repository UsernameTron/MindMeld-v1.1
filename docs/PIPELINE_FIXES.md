# MindMeld Agent Pipeline 

## Overview

The MindMeld agent pipeline provides a robust framework for executing various AI agents against code repositories. This document outlines the recent improvements made to the system.

## Core Components

### Input Validation

Each agent now has clearly defined input type requirements:
- File-based agents: Require file paths and validate that the file exists
- Directory-based agents: Require directory paths and validate that the directory exists
- Integer-based agents: Require integer values and validate the type

### Schema Standardization

All agent outputs now conform to a standardized JSON schema defined in `agent_report_schema.json`:
- Required fields: `agent`, `status`, `timestamp`
- Status types: `success`, `error`, `partial_success`
- Conditional requirements: For `status: error`, the `error` field is required; for `status: success`, the `data` field is required

### Error Handling

Error handling is now consistent across all agents with:
- Clear error messages and types
- Proper context in error reports
- Fallback mechanisms when appropriate

## Running Agents

```bash
# Run a specific agent on a file
python run_agent.py CodeDebuggerAgent path/to/file.py

# Run a specific agent on a directory
python run_agent.py DependencyAgent path/to/directory

# Run summarizer agent with integer input
python run_agent.py summarizer 42
```

## Testing

Comprehensive test suites ensure the pipeline is robust:
```bash
# Run all tests
python -m pytest tests/

# Run specific test modules
python -m pytest test_schema_validator.py
python -m pytest tests/test_pipeline_fixes.py
```

## Validation

A GitHub Actions workflow automatically validates agent reports against the schema:
- Runs on each push to main and develop branches
- Validates all agent report JSON files
- Fails if any reports don't match the schema

## Integration with FastAPI

The FastAPI app provides REST endpoints for agent execution:
- Input validation on all endpoints
- Consistent error responses
- Background task support for long-running operations

## Error Types

The system defines a hierarchy of error types for precise error handling:
- `AgentError`: Base class for all agent errors
- `ValidationError`: For input validation issues
- `InputValidationError`: For type validation issues
- `SchemaValidationError`: For schema compliance issues
- And more specific error types...

## Future Improvements

Planned improvements include:
- Better caching of results
- Agent orchestration for complex workflows
- Expanded CI/CD integration
- Comprehensive regression tests
