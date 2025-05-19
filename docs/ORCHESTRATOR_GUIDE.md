# OrchestratorAgent Guide

The OrchestratorAgent in MindMeld is designed to coordinate the activities of multiple specialized agents to perform complex tasks. This guide explains how to use the OrchestratorAgent, define workflows, and create custom agent orchestration solutions.

## Overview

The OrchestratorAgent serves as a central coordinator that:

1. Manages workflows consisting of multiple steps
2. Routes data between different agents
3. Handles conditional branching and transformations
4. Aggregates results from multiple agents

## Basic Usage

### Command Line Interface

The `run_workflow.py` script provides a command-line interface to run workflows:

```bash
# Run code quality workflow on a file
./run_workflow.py --workflow code_quality --path src/utils/file_operations.py

# Run dependency analysis on a directory
./run_workflow.py --workflow dependency_analysis --path src

# Generate tests for a file
./run_workflow.py --workflow test_coverage --path src/agents/implementations/dependency_management.py
```

### Programmatic Usage

You can also use the OrchestratorAgent programmatically:

```python
from src.agents.implementations.orchestrator import OrchestratorAgent
from src.agents.implementations.code_debug import CodeDebugAgent
from src.agents.workflows.code_quality import WORKFLOWS

# Initialize agents
orchestrator = OrchestratorAgent()
code_debug = CodeDebugAgent()

# Register agent with orchestrator
orchestrator.register_agent_instance("code_debug", code_debug)

# Register workflows
for name, workflow in WORKFLOWS.items():
    orchestrator.register_workflow(name, workflow)

# Execute a workflow
result = orchestrator.process({
    "workflow": "code_quality",
    "input": {
        "code": "def example(): pass",
        "file_path": "example.py"
    }
})
```

## Workflow Definitions

A workflow is defined as a dictionary with the following structure:

```python
workflow = {
    "name": "workflow_name",
    "description": "Workflow description",
    "version": "1.0",
    "steps": [
        # Step definitions
    ]
}
```

### Step Types

The OrchestratorAgent supports three types of steps:

#### 1. Agent Steps

Agent steps execute a registered agent with specific inputs:

```python
{
    "id": "debug",
    "type": "agent",
    "agent": "code_debug",
    "description": "Detect bugs in code",
    "input": {
        # Static input data
    },
    "dynamic_input": {
        # Map keys to paths in workflow state
        "code": "input.code"
    }
}
```

#### 2. Condition Steps

Condition steps enable branching logic:

```python
{
    "id": "check_issues",
    "type": "condition",
    "description": "Check if there are issues",
    "condition": {
        "type": "not_empty",
        "path": "results.debug.issues"
    },
    "then": {
        # Step to execute if condition is true
    },
    "else": {
        # Step to execute if condition is false
    }
}
```

Supported condition types:
- `exists`: Check if a value exists
- `equals`: Check if a value equals an expected value
- `not_empty`: Check if a value is not empty

#### 3. Transform Steps

Transform steps manipulate data:

```python
{
    "id": "merge_results",
    "type": "transform",
    "transform_type": "merge",
    "description": "Merge results from all agents",
    "input": [
        "results.debug",
        "results.dependency"
    ]
}
```

Supported transform types:
- `merge`: Merge multiple dictionaries
- `filter`: Filter a list based on criteria
- `map`: Extract specific fields from objects in a list

## Creating Custom Workflows

You can create and register custom workflows:

```python
# Define the workflow
custom_workflow = {
    "name": "quick_debug",
    "description": "Quick debugging workflow",
    "version": "1.0",
    "steps": [
        # Step definitions
    ]
}

# Register the workflow
orchestrator.register_workflow("quick_debug", custom_workflow)
```

## Workflow State

The workflow state contains:

- `input`: The input data for the workflow
- `results`: Results from completed steps
- `options`: Configuration options
- `current_step`: The current step index
- `completed_steps`: IDs of completed steps
- `errors`: Any errors that occurred

## Accessing Data from Workflow State

In dynamic inputs and conditions, you can access data using dot notation:

- `input.code`: Access the code field in the input data
- `results.debug.issues`: Access the issues field in the debug step results

## Example Workflows

See `src/agents/workflows/code_quality.py` for example workflow definitions:

- `CODE_QUALITY_WORKFLOW`: Combines code debugging, dependency management, and test generation
- `TEST_COVERAGE_WORKFLOW`: Generates and validates tests
- `DEPENDENCY_WORKFLOW`: Analyzes dependencies with conditional steps

## Error Handling

Set the `continue_on_error` option to `True` to continue workflow execution even if some steps fail:

```python
result = orchestrator.process({
    "workflow": "code_quality",
    "input": { ... },
    "options": {
        "continue_on_error": True
    }
})
```
