import os
import tempfile
from typing import Any

import pytest

from packages.agents import DependencyAgent

# Import the ClaudeAPIClient from the correct location
from packages.agents.claude_agents.api.client import ClaudeAPIClient


class MockClaudeAPIClient(ClaudeAPIClient):
    def chat(self, *args, **kwargs) -> Any:
        return {"output": "mock response"}


def test_analyze_deps_empty_directory():
    from packages.agents.claude_agents.agents.dependency_management import (
        DependencyManagementAgent,
    )

    agent = DependencyManagementAgent(
        name="test_dependency_agent", role="test", api_client=MockClaudeAPIClient()
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        result = agent.process({"file_path": tmpdir})
        assert "installation_commands" in result
        assert "missing_dependencies" in result
        assert "required_dependencies" in result
        assert len(result["required_dependencies"]) == 0


def test_analyze_deps_with_imports():
    from packages.agents.claude_agents.agents.dependency_management import (
        DependencyManagementAgent,
    )

    agent = DependencyManagementAgent(
        name="test_dependency_agent", role="test", api_client=MockClaudeAPIClient()
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, "w") as f:
            f.write("import os\nimport sys\nfrom pathlib import Path")
        result = agent.process({"file_path": tmpdir})
        assert "required_dependencies" in result
        # Standard libraries like os, sys, pathlib aren't listed as dependencies
        # We'll just check that the output format is correct
