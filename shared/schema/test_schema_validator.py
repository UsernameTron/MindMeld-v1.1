#!/usr/bin/env python3
import json
import os
import sys
import tempfile
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schema_validator import normalize_agent_output, validate_agent_output


class TestAgentValidation(unittest.TestCase):
    """Test input validation and error handling."""

    def test_validation_file_not_found(self):
        """Test validation with non-existent file."""

        from run_agent import validate_input

        # Test with non-existent file for CodeDebuggerAgent
        result = validate_input("CodeDebuggerAgent", "nonexistent.py")
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "error")
        self.assertIn("not found", result["error"]["message"])

    def test_validation_directory_for_file_agent(self):
        """Test validation with directory for file-only agent."""

        from run_agent import validate_input

        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Test with directory for CodeDebuggerAgent
            result = validate_input("CodeDebuggerAgent", tmpdir)
            self.assertIsNotNone(result)
            self.assertEqual(result["status"], "error")
            self.assertIn("directory", result["error"]["message"])

    def test_validation_non_integer_for_summarizer(self):
        """Test validation with non-integer for summarizer agent."""

        from run_agent import validate_input

        # Test with string for summarizer
        result = validate_input("summarizer", "not_an_integer")
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "error")
        self.assertIn("expected integer", result["error"]["message"])


class TestSchemaValidation(unittest.TestCase):
    """Test schema validation and normalization."""

    def test_normalize_agent_output(self):
        """Test normalizing different agent outputs."""
        # Test with error output
        error_output = {"error": "Test error"}
        normalized = normalize_agent_output(error_output, "TestAgent", "test_payload")
        self.assertEqual(normalized["status"], "error")
        self.assertEqual(normalized["error"]["message"], "Test error")

        # Test with fixed output
        fixed_output = {"fixed": True, "diagnostics": "No issues"}
        normalized = normalize_agent_output(fixed_output, "TestAgent", "test_payload")
        self.assertEqual(normalized["status"], "success")
        self.assertEqual(normalized["data"]["fixed"], True)
        self.assertEqual(normalized["data"]["diagnostics"], "No issues")

        # Test with dependencies output
        deps_output = {"dependencies": {"file.py": ["os", "sys"]}}
        normalized = normalize_agent_output(deps_output, "TestAgent", "test_payload")
        self.assertEqual(normalized["status"], "success")
        self.assertEqual(normalized["data"]["dependencies"], {"file.py": ["os", "sys"]})

    def test_validate_agent_output(self):
        """Test validating agent output against schema."""
        # Valid output
        valid_output = {
            "agent": "TestAgent",
            "status": "success",
            "timestamp": 123456789,
            "payload": "test_payload",
            "data": {"result": "Test result"},
        }

        # Create temporary schema file for testing
        schema_json = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "agent": {"type": "string"},
                "status": {
                    "type": "string",
                    "enum": ["success", "error", "partial_success"],
                },
                "timestamp": {"type": "integer"},
                "payload": {"type": "string"},
                "data": {"type": "object"},
            },
            "required": ["agent", "status", "timestamp"],
        }

        with tempfile.NamedTemporaryFile(
            mode="w+", suffix=".json", delete=False
        ) as temp:
            json.dump(schema_json, temp)
            temp_path = temp.name

        try:
            is_valid, error = validate_agent_output(valid_output, temp_path)
            self.assertTrue(is_valid)
            self.assertIsNone(error)

            # Invalid output (missing required field)
            invalid_output = {
                "agent": "TestAgent",
                # Missing status
                "timestamp": 123456789,
                "payload": "test_payload",
                "data": {"result": "Test result"},
            }
            is_valid, error = validate_agent_output(invalid_output, temp_path)
            self.assertFalse(is_valid)
            self.assertIn("status", error)
        finally:
            os.unlink(temp_path)


class TestSummarizerAgent(unittest.TestCase):
    """Test the summarizer agent's integer handling."""

    def test_summarizer_with_integer(self):
        """Test summarizer agent with valid integer input."""
        from packages.agents.AgentFactory import AGENT_REGISTRY

        # Get the summarizer agent from registry
        summarizer_agent_factory = AGENT_REGISTRY.get("summarizer")
        self.assertIsNotNone(summarizer_agent_factory)

        # Create agent instance
        summarizer_agent = summarizer_agent_factory()

        # Test with valid integer
        try:
            result = summarizer_agent.run(42)
            self.assertIsInstance(result, dict)
            self.assertIn("summary_id", result)
            self.assertEqual(result["summary_id"], 42)
        except Exception as e:
            self.fail(f"Summarizer agent failed with valid integer: {e}")

    def test_summarizer_with_string_integer(self):
        """Test summarizer agent with string that can be converted to integer."""
        from packages.agents.AgentFactory import AGENT_REGISTRY

        # Get the summarizer agent from registry
        summarizer_agent_factory = AGENT_REGISTRY.get("summarizer")
        summarizer_agent = summarizer_agent_factory()

        # Test with string integer
        try:
            result = summarizer_agent.run("42")
            self.assertIsInstance(result, dict)
            self.assertIn("summary_id", result)
            self.assertEqual(result["summary_id"], 42)
        except Exception as e:
            self.fail(f"Summarizer agent failed with convertible string: {e}")

    def test_summarizer_with_invalid_input(self):
        """Test summarizer agent with invalid input (should raise ValueError)."""
        from packages.agents.AgentFactory import AGENT_REGISTRY

        # Get the summarizer agent from registry
        summarizer_agent_factory = AGENT_REGISTRY.get("summarizer")
        summarizer_agent = summarizer_agent_factory()

        # Test with invalid input
        with self.assertRaises(ValueError):
            summarizer_agent.run("not_an_integer")


if __name__ == "__main__":
    unittest.main()
