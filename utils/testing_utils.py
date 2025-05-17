#!/usr/bin/env python3
"""
Testing Utilities for MindMeld Framework

This module provides comprehensive testing support for MindMeld agents
including mocking, fixtures, and testing assertions.
"""

import json
import os
import shutil
import tempfile
import unittest.mock as mock
from pathlib import Path
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar, Union

# Type variable for generic testing
T = TypeVar("T")


class MockLLMResponse:
    """Mock response from LLM API calls."""

    def __init__(self, content: str, status_code: int = 200):
        """
        Initialize a mock LLM response.

        Args:
            content: Text content of the response
            status_code: HTTP status code
        """
        self.content = content
        self.status_code = status_code

    def json(self) -> Dict[str, Any]:
        """
        Get response as JSON.

        Returns:
            Parsed JSON response
        """
        return {"response": self.content}

    def __str__(self) -> str:
        """String representation."""
        return self.content


class MockOllamaClient:
    """Mock Ollama API client for testing."""

    def __init__(self, responses: Dict[str, Union[str, Dict[str, Any]]] = None):
        """
        Initialize mock Ollama client.

        Args:
            responses: Dictionary mapping prompt prefixes to responses
        """
        self.responses = responses or {}
        self.call_history = []
        self.available_models = ["phi3.5:latest", "llama2:13b"]

    def generate(
        self, prompt: str, model: str = "phi3.5:latest", **kwargs
    ) -> MockLLMResponse:
        """
        Mock generate method.

        Args:
            prompt: Input prompt
            model: Model name
            **kwargs: Additional arguments

        Returns:
            Mock LLM response
        """
        self.call_history.append({"prompt": prompt, "model": model, "kwargs": kwargs})

        # Try to find a matching response
        for key, response in self.responses.items():
            if prompt.startswith(key):
                if isinstance(response, str):
                    return MockLLMResponse(response)
                elif isinstance(response, dict):
                    return response

        # Default response if no match
        return MockLLMResponse(f"Mock response for: {prompt[:30]}...")

    def list_models(self) -> Dict[str, List[str]]:
        """
        Mock list_models method.

        Returns:
            Dictionary of available models
        """
        return {"models": [{"name": model} for model in self.available_models]}

    def add_model(self, model_name: str) -> None:
        """
        Add a model to available models.

        Args:
            model_name: Name of model to add
        """
        if model_name not in self.available_models:
            self.available_models.append(model_name)

    def remove_model(self, model_name: str) -> None:
        """
        Remove a model from available models.

        Args:
            model_name: Name of model to remove
        """
        if model_name in self.available_models:
            self.available_models.remove(model_name)


class AgentTestCase:
    """Base class for agent test cases with useful testing utilities."""

    def __init__(self):
        """Initialize the test case."""
        self.temp_dirs = []

    def create_temp_directory(self) -> str:
        """
        Create a temporary directory for testing.

        Returns:
            Path to the temporary directory
        """
        temp_dir = tempfile.mkdtemp()
        self.temp_dirs.append(temp_dir)
        return temp_dir

    def create_temp_file(self, content: str, suffix: str = ".py") -> str:
        """
        Create a temporary file for testing.

        Args:
            content: Content to write to file
            suffix: File extension

        Returns:
            Path to the temporary file
        """
        fd, path = tempfile.mkstemp(suffix=suffix)
        with os.fdopen(fd, "w") as f:
            f.write(content)
        return path

    def cleanup(self) -> None:
        """Clean up temporary files and directories."""
        for temp_dir in self.temp_dirs:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def __del__(self):
        """Ensure cleanup on object destruction."""
        self.cleanup()

    def mock_agent_dependencies(self, agent_cls, **kwargs) -> mock.MagicMock:
        """
        Mock agent dependencies for isolated testing.

        Args:
            agent_cls: Agent class to mock
            **kwargs: Additional mocks to inject

        Returns:
            Mock object
        """
        with mock.patch.multiple(agent_cls, **kwargs):
            return mock.MagicMock(spec=agent_cls)

    def assert_valid_output_schema(
        self, output: Dict[str, Any], schema_path: Optional[str] = None
    ) -> None:
        """
        Assert that agent output conforms to schema.

        Args:
            output: Agent output to validate
            schema_path: Optional path to schema

        Raises:
            AssertionError: If output doesn't conform to schema
        """
        from utils.schema_validator import validate_agent_output

        valid, error = validate_agent_output(output, schema_path)
        assert valid, f"Schema validation failed: {error}"

    def create_test_codebase(self, files: Dict[str, str]) -> str:
        """
        Create a test codebase with specified files.

        Args:
            files: Dictionary mapping file paths to content

        Returns:
            Root directory of test codebase
        """
        root_dir = self.create_temp_directory()

        for file_path, content in files.items():
            full_path = os.path.join(root_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, "w") as f:
                f.write(content)

        return root_dir


def patch_llm_calls(
    responses: Dict[str, Union[str, Dict[str, Any]]] = None
) -> Callable:
    """
    Decorator to patch LLM API calls.

    Args:
        responses: Dictionary mapping prompt prefixes to responses

    Returns:
        Decorator function
    """

    def decorator(func):
        @mock.patch("utils.llm_client.call_llm")
        def wrapper(mock_call_llm, *args, **kwargs):
            mock_client = MockOllamaClient(responses)

            def mock_llm_call(prompt, *call_args, **call_kwargs):
                return mock_client.generate(prompt, *call_args, **call_kwargs)

            mock_call_llm.side_effect = mock_llm_call
            return func(*args, **kwargs)

        return wrapper

    return decorator


def assert_agent_report_format(report: Dict[str, Any]) -> None:
    """
    Assert that report has the expected format.

    Args:
        report: Agent report to check

    Raises:
        AssertionError: If report format is invalid
    """
    assert "agent" in report, "Report missing 'agent' field"
    assert "timestamp" in report, "Report missing 'timestamp' field"
    assert "metadata" in report, "Report missing 'metadata' field"
    assert "status" in report, "Report missing 'status' field"

    if report["status"] == "success":
        assert "data" in report, "Success report missing 'data' field"
    elif report["status"] == "error":
        assert "error" in report, "Error report missing 'error' field"
    else:
        assert False, f"Invalid status: {report['status']}"
