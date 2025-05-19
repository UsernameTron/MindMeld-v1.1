#!/usr/bin/env python3
"""
Example script demonstrating how to use the OrchestratorAgent programmatically.
"""

import json
import os

from src.agents.implementations.code_debug import CodeDebugAgent
from src.agents.implementations.dependency_management import DependencyManagementAgent
from src.agents.implementations.orchestrator import OrchestratorAgent
from src.agents.implementations.test_generator import TestGeneratorAgent
from src.agents.workflows.code_quality import WORKFLOWS


def run_custom_workflow(file_path, workflow_name="code_quality"):
    """
    Run a workflow on a specific file using the OrchestratorAgent.

    Args:
        file_path: Path to the file to analyze
        workflow_name: Name of the workflow to run

    Returns:
        Results dictionary from the workflow execution
    """
    # Initialize agents
    orchestrator = OrchestratorAgent()
    code_debug = CodeDebugAgent()
    dependency = DependencyManagementAgent()
    test_generator = TestGeneratorAgent()

    # Register agents with orchestrator
    orchestrator.register_agent_instance("code_debug", code_debug)
    orchestrator.register_agent_instance("dependency_management", dependency)
    orchestrator.register_agent_instance("test_generator", test_generator)

    # Register workflows
    for name, workflow in WORKFLOWS.items():
        orchestrator.register_workflow(name, workflow)

    # Prepare input data
    with open(file_path, "r") as f:
        code = f.read()

    input_data = {
        "workflow": workflow_name,
        "input": {"code": code, "file_path": file_path},
        "options": {"continue_on_error": True},
    }

    # Execute workflow
    result = orchestrator.process(input_data)
    return result


def create_custom_workflow():
    """
    Create and register a custom workflow with the OrchestratorAgent.
    """
    # Initialize orchestrator
    orchestrator = OrchestratorAgent()

    # Create agent instances
    code_debug = CodeDebugAgent()
    dependency = DependencyManagementAgent()

    # Register agents
    orchestrator.register_agent_instance("code_debug", code_debug)
    orchestrator.register_agent_instance("dependency", dependency)

    # Define custom workflow
    custom_workflow = {
        "name": "quick_debug",
        "description": "Quick debug workflow that only checks for bugs and dependency issues",
        "version": "1.0",
        "steps": [
            {
                "id": "debug",
                "type": "agent",
                "agent": "code_debug",
                "description": "Detect bugs and issues in the code",
                "input": {},  # Will be filled from workflow input
            },
            {
                "id": "conditional_dependency_check",
                "type": "condition",
                "description": "Check if debug found issues, then check dependencies",
                "condition": {"type": "not_empty", "path": "results.debug.issues"},
                "then": {
                    "id": "dependency",
                    "type": "agent",
                    "agent": "dependency",
                    "description": "Check for dependency issues",
                },
            },
        ],
    }

    # Register custom workflow
    orchestrator.register_workflow("quick_debug", custom_workflow)

    # Example usage with a file
    file_path = "src/agents/implementations/orchestrator.py"
    with open(file_path, "r") as f:
        code = f.read()

    result = orchestrator.process(
        {"workflow": "quick_debug", "input": {"code": code, "file_path": file_path}}
    )

    print(json.dumps(result, indent=2))

    return result


if __name__ == "__main__":
    # Example 1: Run an existing workflow
    result = run_custom_workflow("src/utils/file_operations.py")
    print("Code Quality Results:")
    print(json.dumps(result, indent=2))

    # Example 2: Create and run a custom workflow
    print("\nCustom Workflow Results:")
    custom_result = create_custom_workflow()
