#!/usr/bin/env python3
"""
Unit tests for TestGeneratorAgent using the new utility modules.
"""

import json
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from utils.error_handling import FileProcessingError, LLMCallError
from utils.file_operations import read_file, write_file

from packages.agents.AgentFactory import AGENT_REGISTRY


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
        self.agent_creator = AGENT_REGISTRY.get("test_generator")
        self.assertIsNotNone(
            self.agent_creator, "TestGeneratorAgent not found in registry"
        )
        self.agent = self.agent_creator()

    def tearDown(self):
        """Clean up after tests."""
        # Remove the test file
        if self.test_file.exists():
            self.test_file.unlink()

    @patch("packages.agents.advanced_reasoning.agents.Client")
    def test_agent_can_generate_tests(self, mock_client):
        """Test that the agent can generate tests for a Python file."""
        # Mock the LLM client to return a sample response
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.generate.return_value = {
            "response": """
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
        result = self.agent.generate_report(str(self.test_file))

        # Verify that the result has the expected structure
        self.assertIn("status", result)
        self.assertEqual(result["status"], "success")
        self.assertIn("data", result)
        self.assertIn("tests", result["data"])

        # Verify that the generated tests include our mocked content
        self.assertIn("test_add", result["data"]["tests"])
        self.assertIn("test_subtract", result["data"]["tests"])

    @patch("packages.agents.advanced_reasoning.agents.Client")
    def test_agent_handles_llm_errors(self, mock_client):
        """Test that the agent properly handles LLM errors."""
        # Mock the LLM client to raise an exception
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        mock_instance.generate.side_effect = Exception("LLM connection failed")

        # Call the agent with the test file
        result = self.agent.generate_report(str(self.test_file))

        # Verify that the result has the expected error structure
        self.assertIn("status", result)
        self.assertEqual(result["status"], "error")
        self.assertIn("error", result)
        self.assertIn("message", result["error"])
        self.assertIn("LLM connection failed", result["error"]["message"])

    def test_agent_handles_missing_file(self):
        """Test that the agent properly handles missing files."""
        # Call the agent with a non-existent file
        result = self.agent.generate_report("non_existent_file.py")

        # Verify that the result has the expected error structure
        self.assertIn("status", result)
        self.assertEqual(result["status"], "error")
        self.assertIn("error", result)
        self.assertIn("message", result["error"])
        self.assertIn("File not found", result["error"]["message"])


if __name__ == "__main__":
    unittest.main()
