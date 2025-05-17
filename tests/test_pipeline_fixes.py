#!/usr/bin/env python3
"""
Comprehensive tests for the MindMeld agent pipeline fixes.
This module tests:
1. Input validation
2. Schema standardization
3. Error handling
4. Type conversion
"""

import unittest
import sys
import os
import tempfile
import json
import time
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schema_validator import normalize_agent_output, validate_agent_output
from run_agent import validate_input
from packages.agents.AgentFactory import AGENT_REGISTRY, AGENT_INPUT_TYPES
from exceptions import ValidationError, InputValidationError, SchemaValidationError

class TestInputValidation(unittest.TestCase):
    """Test input validation for different agent types."""
    
    def test_file_validation(self):
        """Test validation for file-input agents."""
        # Test with non-existent file
        result = validate_input("CodeDebuggerAgent", "nonexistent.py")
        self.assertEqual(result["status"], "error")
        self.assertIn("not found", result["error"]["message"])
        
        # Test with directory when file expected
        with tempfile.TemporaryDirectory() as tmpdir:
            result = validate_input("CodeDebuggerAgent", tmpdir)
            self.assertEqual(result["status"], "error")
            self.assertIn("directory", result["error"]["message"])
        
        # Test with valid file
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tmpfile:
            tmpfile.write(b"print('hello')")
            tmpfile_path = tmpfile.name
        
        try:
            result = validate_input("CodeDebuggerAgent", tmpfile_path)
            self.assertIsNone(result)  # None means validation passed
        finally:
            os.unlink(tmpfile_path)
    
    def test_directory_validation(self):
        """Test validation for directory-input agents."""
        # Test with non-existent directory
        result = validate_input("DependencyAgent", "nonexistent_dir")
        self.assertEqual(result["status"], "error")
        self.assertIn("not found", result["error"]["message"])
        
        # Test with file when directory expected
        with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
            tmpfile.write(b"test")
            tmpfile_path = tmpfile.name
        
        try:
            result = validate_input("DependencyAgent", tmpfile_path)
            self.assertEqual(result["status"], "error")
            self.assertIn("directory", result["error"]["message"])
        finally:
            os.unlink(tmpfile_path)
        
        # Test with valid directory
        with tempfile.TemporaryDirectory() as tmpdir:
            result = validate_input("DependencyAgent", tmpdir)
            self.assertIsNone(result)  # None means validation passed
    
    def test_integer_validation(self):
        """Test validation for integer-input agents."""
        # Test with non-integer string
        result = validate_input("summarizer", "not_an_integer")
        self.assertEqual(result["status"], "error")
        self.assertIn("integer", result["error"]["message"])
        
        # Test with valid integer string
        result = validate_input("summarizer", "42")
        self.assertIsNone(result)  # None means validation passed
        
        # Test with integer
        result = validate_input("summarizer", 42)
        self.assertIsNone(result)  # None means validation passed

class TestSchemaCompliance(unittest.TestCase):
    """Test schema compliance of normalized outputs."""
    
    def test_error_normalization(self):
        """Test error normalization."""
        # Create an error result
        error_result = normalize_agent_output(
            {"error": "Something went wrong"},
            "TestAgent",
            "test_input",
            int(time.time()),
            0.5,
            "test-job-id"
        )
        
        # Validate against schema
        valid, error = validate_agent_output(error_result)
        self.assertTrue(valid, f"Error normalization failed: {error}")
        self.assertEqual(error_result["status"], "error")
        self.assertIn("error", error_result)
        self.assertIn("message", error_result["error"])
    
    def test_success_normalization(self):
        """Test success normalization."""
        # Create a success result
        success_result = normalize_agent_output(
            {"result": "It worked!"},
            "TestAgent",
            "test_input",
            int(time.time()),
            0.5,
            "test-job-id"
        )
        
        # Validate against schema
        valid, error = validate_agent_output(success_result)
        self.assertTrue(valid, f"Success normalization failed: {error}")
        self.assertEqual(success_result["status"], "success")
        self.assertIn("data", success_result)
    
    def test_metadata_inclusion(self):
        """Test that metadata is properly included."""
        # Create a result with metadata
        result = normalize_agent_output(
            {"result": "With metadata"},
            "TestAgent",
            "test_input",
            int(time.time()),
            0.5,
            "test-job-id"
        )
        
        # Check metadata fields
        self.assertIn("metadata", result)
        self.assertIn("agent", result["metadata"])
        self.assertIn("timestamp", result["metadata"])
        self.assertIn("job_id", result["metadata"])
        self.assertIn("system_info", result["metadata"])
        self.assertIn("model_info", result["metadata"])

class TestAgentImplementations(unittest.TestCase):
    """Test specific agent implementations for fixes."""
    
    def test_summarizer_agent(self):
        """Test the fixed summarizer agent."""
        # Get the summarizer agent
        summarizer_factory = AGENT_REGISTRY.get("summarizer")
        self.assertIsNotNone(summarizer_factory, "Summarizer agent not found in registry")
        
        # Create agent instance
        summarizer = summarizer_factory()
        
        # Test with integer
        result = summarizer.run(42)
        self.assertIsInstance(result, dict)
        self.assertIn("summary_id", result)
        self.assertEqual(result["summary_id"], 42)
        
        # Test with string that can be converted
        result = summarizer.run("42")
        self.assertIsInstance(result, dict)
        self.assertIn("summary_id", result)
        self.assertEqual(result["summary_id"], 42)
        
        # Test with invalid input
        with self.assertRaises(ValueError):
            summarizer.run("not_an_integer")
    
    def test_code_debugger_agent(self):
        """Test CodeDebuggerAgent with file validation."""
        # Check if agent exists in registry
        debugger_class = AGENT_REGISTRY.get("CodeDebuggerAgent")
        self.assertIsNotNone(debugger_class, "CodeDebuggerAgent not found in registry")
        
        # Check input type is set correctly
        self.assertEqual(AGENT_INPUT_TYPES.get("CodeDebuggerAgent"), "file", 
                         "CodeDebuggerAgent should be marked as requiring file input")

if __name__ == "__main__":
    unittest.main()
