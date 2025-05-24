#!/usr/bin/env python3
"""
Unit tests for TestGeneratorAgent using the new utility modules.
"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


class MockClaudeAPIClient:
    def chat(self, *args, **kwargs):
        return {"output": "mock response"}


class TestGeneratorAgentTests(unittest.TestCase):
    """Test suite for TestGeneratorAgent."""

    def setUp(self):
        """Set up test environment."""
        # Make sure test directory exists
        self.test_dir = Path(__file__).parent / "test_data"
        self.test_dir.mkdir(exist_ok=True)

        # Create a sample Python file for testing
        self.test_file = self.test_dir / "sample.py"
        sample_code = """
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
"""
        with open(self.test_file, "w") as f:
            f.write(sample_code)

        # Get the agent instance
        from packages.agents.claude_agents.agents.test_generator import (
            TestGeneratorAgent,
        )

        self.agent = TestGeneratorAgent(
            name="test_generator",
            role="test",
            api_client=MockClaudeAPIClient(),
        )

    def tearDown(self):
        """Clean up after tests."""
        # Remove the test file
        if self.test_file.exists():
            self.test_file.unlink()

    @patch(
        "packages.agents.claude_agents.agents.test_generator.TestGeneratorAgent._call_claude"
    )
    def test_agent_can_generate_tests(self, mock_call_claude):
        """Test that the agent can generate tests for a Python file."""
        # Mock the _call_claude method to return a sample response
        mock_call_claude.return_value = {
            "output": """
import unittest

def test_add():
    assert add(1, 2) == 3
    assert add(-1, 1) == 0

def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(10, 10) == 0
"""
        }

        # Call the agent with the test file
        result = self.agent.process({"file_path": str(self.test_file)})

        # Verify that the result has the expected structure
        self.assertIn("status", result)
        self.assertEqual(result["status"], "success")
        self.assertIn("data", result)
        self.assertIn("tests", result["data"])

        # Verify that the generated tests include our mocked content
        self.assertIn("test_add", result["data"]["tests"])
        self.assertIn("test_subtract", result["data"]["tests"])

    @patch("packages.agents.claude_agents.api.client.ClaudeAPIClient")
    def test_agent_handles_llm_errors(self, mock_client):
        """Test that the agent properly handles LLM errors."""
        # Mock the LLM client to raise an exception
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.chat.side_effect = Exception("LLM connection failed")

        # Call the agent with the test file
        result = self.agent.process({"file_path": str(self.test_file)})

        # Verify that the result has the expected error structure
        self.assertIn("status", result)
        self.assertEqual(result["status"], "error")
        self.assertIn("error", result)
        self.assertIn("message", result["error"])
        self.assertIn("LLM connection failed", result["error"]["message"])

    def test_agent_handles_missing_file(self):
        """Test that the agent properly handles missing files."""
        # Call the agent with a non-existent file
        result = self.agent.process({"file_path": "non_existent_file.py"})

        # Verify that the result has the expected error structure
        self.assertIn("status", result)
        self.assertEqual(result["status"], "error")
        self.assertIn("error", result)
        self.assertIn("message", result["error"])
        self.assertIn("File not found", result["error"]["message"])


if __name__ == "__main__":
    unittest.main()
