"""
Tests for the standardized dependency agent implementation.
"""

from unittest.mock import MagicMock, patch

import pytest

from packages.agents.implementations.dependency import DependencyAgent


class TestDependencyAgent:
    """Test cases for DependencyAgent."""

    @pytest.fixture
    def mock_api_client(self):
        """Create a mock API client for testing."""
        client = MagicMock()
        return client

    @pytest.fixture
    def dependency_agent(self, mock_api_client):
        """Create a dependency agent instance for testing."""
        return DependencyAgent(
            name="TestDependencyAgent", role="testing", api_client=mock_api_client
        )

    def test_init(self, dependency_agent):
        """Test agent initialization."""
        assert dependency_agent.name == "TestDependencyAgent"
        assert dependency_agent.role == "testing"
        assert dependency_agent.capabilities is not None
        assert "code" in dependency_agent.capabilities["supported_inputs"]

    def test_validate_input_valid(self, dependency_agent):
        """Test input validation with valid inputs."""
        # Test with code
        assert dependency_agent.validate_input({"code": "import pandas"})

        # Test with requirements
        assert dependency_agent.validate_input(
            {"requirements_content": "pandas==1.0.0"}
        )

        # Test with error traceback
        assert dependency_agent.validate_input(
            {"error_traceback": "ModuleNotFoundError: No module named 'torch'"}
        )

        # Test with multiple inputs
        assert dependency_agent.validate_input(
            {"code": "import pandas", "requirements_content": "pandas==1.0.0"}
        )

    def test_validate_input_invalid(self, dependency_agent):
        """Test input validation with invalid inputs."""
        # Empty dict
        assert not dependency_agent.validate_input({})

        # Non-dict input
        assert not dependency_agent.validate_input("not a dict")

        # Dict with wrong keys
        assert not dependency_agent.validate_input({"wrong_key": "value"})

    def test_analyze_code(self, dependency_agent):
        """Test code analysis for dependencies."""
        code = """
        import pandas as pd
        import numpy as np
        from sklearn.model_selection import train_test_split
        import os
        import sys

        def process_data(df):
            return df.fillna(0)
        """

        result = dependency_agent._analyze_code(code)

        assert "pandas" in result["required_dependencies"]
        assert "numpy" in result["required_dependencies"]
        assert "sklearn" in result["required_dependencies"]
        # Standard library modules should be excluded
        assert "os" not in result["required_dependencies"]
        assert "sys" not in result["required_dependencies"]

    def test_analyze_error_traceback(self, dependency_agent):
        """Test error traceback analysis."""
        error = """
        Traceback (most recent call last):
          File "script.py", line 10, in <module>
            import torch
        ModuleNotFoundError: No module named 'torch'
        """

        result = {"missing_dependencies": [], "installation_commands": []}
        dependency_agent._analyze_error_traceback(error, result)

        assert "torch" in result["missing_dependencies"]
        assert any(
            "pip install torch" in cmd for cmd in result["installation_commands"]
        )

    def test_analyze_requirements(self, dependency_agent):
        """Test requirements analysis for conflicts and vulnerabilities."""
        requirements = """
        pandas==1.0.0
        numpy>=1.18.0
        tensorflow==2.4.0
        tensorflow-gpu==2.5.0
        django==2.2.0
        """

        result = {"version_conflicts": [], "vulnerabilities": []}
        dependency_agent._analyze_requirements(requirements, result)

        # Should detect TensorFlow version conflict
        assert any(
            conflict["package"] == "tensorflow"
            for conflict in result["version_conflicts"]
        )

        # Should detect Django vulnerability
        assert any(vuln["package"] == "django" for vuln in result["vulnerabilities"])

    def test_process_with_code(self, dependency_agent):
        """Test full processing with code input."""
        with patch.object(dependency_agent, "_analyze_code") as mock_analyze:
            mock_analyze.return_value = {
                "required_dependencies": ["pandas", "numpy"],
                "missing_dependencies": ["pandas"],
            }

            result = dependency_agent.process({"code": "import pandas\nimport numpy"})

            assert result["status"] == "success"
            assert "pandas" in result["data"]["required_dependencies"]
            assert "pandas" in result["data"]["missing_dependencies"]
            assert any(
                "pip install" in cmd for cmd in result["data"]["installation_commands"]
            )

    def test_process_with_error(self, dependency_agent):
        """Test process method with error handling."""
        with patch.object(
            dependency_agent, "_execute_analysis", side_effect=Exception("Test error")
        ):
            result = dependency_agent.process({"code": "import something"})

            assert result["status"] == "error"
            assert "Test error" in result["message"]

    def test_generate_install_commands(self, dependency_agent):
        """Test installation command generation."""
        results = {"missing_dependencies": ["pandas", "numpy", "matplotlib"]}
        commands = dependency_agent.generate_install_commands(results)

        assert len(commands) == 1
        assert "pip install pandas numpy matplotlib" in commands[0]

        # Test with empty list
        assert (
            dependency_agent.generate_install_commands({"missing_dependencies": []})
            == []
        )

        # Test with nested data structure
        nested_results = {"data": {"missing_dependencies": ["requests", "flask"]}}
        nested_commands = dependency_agent.generate_install_commands(nested_results)
        assert "pip install requests flask" in nested_commands[0]
