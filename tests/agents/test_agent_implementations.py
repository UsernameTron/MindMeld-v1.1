"""
Tests for agent implementations using the compatibility layer.
"""

import os
import sys
import unittest

# Add the parent directory to the path so we can import from packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from packages.agents.claude_agents.agents.code_debug import CodeDebugAgent
from packages.agents.claude_agents.agents.dependency_management import (
    DependencyManagementAgent,
)
from packages.agents.claude_agents.agents.test_generator import TestGeneratorAgent
from packages.agents.claude_agents.api.mock_client import MockClaudeAPIClient


class TestAgentImplementations(unittest.TestCase):
    """Test agent implementations with the compatibility layer."""

    def setUp(self):
        """Set up common resources."""
        self.api_client = MockClaudeAPIClient()

    def test_code_debug_agent(self):
        """Test that CodeDebugAgent can be initialized and used."""
        agent = CodeDebugAgent(
            name="debug_agent", role="code debugger", api_client=self.api_client
        )
        self.assertEqual(agent.name, "debug_agent")
        self.assertEqual(agent.role, "code debugger")

        # Test that the agent can process a request
        response = agent.process(
            {"code": "print('Hello, world!')", "file_path": "test.py"}
        )
        self.assertIsNotNone(response)

    def test_test_generator_agent(self):
        """Test that TestGeneratorAgent can be initialized and used."""
        agent = TestGeneratorAgent(
            name="test_gen", role="test generator", api_client=self.api_client
        )
        self.assertEqual(agent.name, "test_gen")
        self.assertEqual(agent.role, "test generator")

        # Test that the agent can process a request
        response = agent.process(
            {
                "code": "def add(a, b): return a + b",
                "file_path": "math_utils.py",
                "test_framework": "pytest",
            }
        )
        self.assertIsNotNone(response)

    def test_dependency_management_agent(self):
        """Test that DependencyManagementAgent can be initialized and used."""
        agent = DependencyManagementAgent(
            name="dep_agent", role="dependency manager", api_client=self.api_client
        )
        self.assertEqual(agent.name, "dep_agent")
        self.assertEqual(agent.role, "dependency manager")

        # Test that the agent can process a request with proper input format
        response = agent.process(
            {
                "code": "import numpy\nimport pandas",
                "file_path": "requirements.txt",
                "project_path": "/tmp/test_project",
            }
        )
        self.assertIsNotNone(response)


if __name__ == "__main__":
    unittest.main()
