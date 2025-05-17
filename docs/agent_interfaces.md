# Agent Interfaces

This document describes the input/output interfaces for each agent in the MindMeld system.

## Overview

All agents follow a common interface pattern:
1. Each agent has a `run()` method that takes specific input parameters
2. Each agent returns a structured output that conforms to the schema defined in `agent_report_schema.json`
3. Agents handle their own input validation and error reporting

## Agent Interface Definitions

### TestGeneratorAgent

Generates pytest tests for Python modules.

**Input:**
- `file_path` (str): Path to the Python file or directory to generate tests for

**Output:**
```json
{
  "agent": "TestGeneratorAgent",
  "status": "success",
  "timestamp": 1621234567,
  "data": {
    "generated_tests": [
      {
        "file_name": "test_example.py",
        "content": "import pytest\nfrom example import Example\n\ndef test_example_method():\n    ..."
      }
    ]
  },
  "metadata": {
    "runtime_seconds": 5.23,
    "model_info": {
      "name": "phi3.5:latest"
    }
  }
}
```

### DependencyAgent

Analyzes code dependencies.

**Input:**
- `file_path` (str): Path to the Python file or directory to analyze dependencies for

**Output:**
```json
{
  "agent": "DependencyAgent",
  "status": "success",
  "timestamp": 1621234567,
  "data": {
    "dependencies": {
      "internal": [
        {"from": "module_a.py", "to": "module_b.py", "imports": ["ClassB", "function_b"]}
      ],
      "external": [
        {"file": "module_a.py", "packages": ["os", "sys", "pandas"]}
      ]
    }
  },
  "metadata": {
    "runtime_seconds": 1.45,
    "model_info": {
      "name": "phi3.5:latest"
    }
  }
}
```

### CodeAnalyzerAgent

Analyzes code structure and quality.

**Input:**
- `file_path` (str): Path to the Python file or directory to analyze

**Output:**
```json
{
  "agent": "CodeAnalyzerAgent",
  "status": "success",
  "timestamp": 1621234567,
  "data": {
    "metrics": {
      "lines_of_code": 256,
      "complexity": {
        "average": 5.2,
        "max": 15
      },
      "classes": 4,
      "functions": 12,
      "imports": 15
    },
    "issues": [
      {
        "file": "example.py",
        "line": 25,
        "severity": "warning",
        "message": "Function has high cyclomatic complexity (15)"
      }
    ]
  },
  "metadata": {
    "runtime_seconds": 2.3,
    "model_info": {
      "name": "phi3.5:latest"
    }
  }
}
```

### CodeDebuggerAgent

Identifies syntax errors and other bugs.

**Input:**
- `file_path` (str): Path to the Python file to debug (must be a file, not a directory)

**Output:**
```json
{
  "agent": "CodeDebuggerAgent",
  "status": "success",
  "timestamp": 1621234567,
  "data": {
    "errors": [
      {
        "file": "buggy.py",
        "line": 42,
        "type": "SyntaxError",
        "message": "Invalid syntax"
      }
    ],
    "is_valid": false
  },
  "metadata": {
    "runtime_seconds": 0.75,
    "model_info": {
      "name": "phi3.5:latest"
    }
  }
}
```

### CodeRepairAgent

Suggests and applies fixes for code issues.

**Input:**
- `file_path` (str): Path to the Python file to repair (must be a file, not a directory)

**Output:**
```json
{
  "agent": "CodeRepairAgent",
  "status": "success",
  "timestamp": 1621234567,
  "data": {
    "fixed": true,
    "changes": [
      {
        "file": "buggy.py",
        "line": 42,
        "original": "if x = 5:",
        "fixed": "if x == 5:"
      }
    ],
    "backup_path": "buggy.py.bak"
  },
  "metadata": {
    "runtime_seconds": 3.1,
    "model_info": {
      "name": "phi3.5:latest"
    }
  }
}
```

### IntegratedCodebaseOptimizer

Orchestrates multiple agents to analyze and optimize a codebase.

**Input:**
- `target_path` (str): Path to the codebase to optimize

**Output:**
```json
{
  "agent": "IntegratedCodebaseOptimizer",
  "status": "success",
  "timestamp": 1621234567,
  "data": {
    "summary": {
      "files_analyzed": 12,
      "issues_found": 5,
      "issues_fixed": 3,
      "tests_generated": 8
    },
    "agent_reports": {
      "CodeAnalyzerAgent": "path/to/analyzer/report.json",
      "CodeDebuggerAgent": "path/to/debugger/report.json",
      "CodeRepairAgent": "path/to/repair/report.json",
      "TestGeneratorAgent": "path/to/test/report.json"
    }
  },
  "metadata": {
    "runtime_seconds": 25.7,
    "model_info": {
      "name": "phi3.5:latest"
    }
  }
}
```

### SummarizerAgent

Summarizes results from other agents.

**Input:**
- `value` (int): An integer value referencing the report ID to summarize

**Output:**
```json
{
  "agent": "summarizer",
  "status": "success",
  "timestamp": 1621234567,
  "data": {
    "summary_id": 42,
    "summary": "Analysis of 12 files complete. Found 5 issues, fixed 3 successfully. Generated 8 unit tests."
  },
  "metadata": {
    "runtime_seconds": 0.5,
    "model_info": {
      "name": "phi3.5:latest"
    }
  }
}
```

## Error Handling

All agents handle errors consistently by returning a structured error response:

```json
{
  "agent": "AgentName",
  "status": "error",
  "timestamp": 1621234567,
  "error": {
    "message": "Descriptive error message",
    "type": "ErrorType",
    "details": "Additional error context"
  },
  "metadata": {
    "runtime_seconds": 0.1,
    "model_info": {
      "name": "phi3.5:latest"
    }
  }
}
```

## Schema Validation

All agent outputs are validated against the schema defined in `agent_report_schema.json`. This ensures consistency and interoperability across the system.

To validate an agent output:

```python
from schema_validator import validate_agent_output

is_valid, error = validate_agent_output(report)
if not is_valid:
    print(f"Invalid report: {error}")
```
