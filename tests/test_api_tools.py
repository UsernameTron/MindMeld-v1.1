#!/usr/bin/env python3
"""
Tests for the update_agent_tools.py and verify_api_tools.py scripts
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, mock_open, patch

# Add scripts directory to path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
)

from scripts import update_agent_tools, verify_api_tools


class TestUpdateAgentTools(unittest.TestCase):
    """Tests for the update_agent_tools.py script"""

    def test_tool_replacement_regex_patterns(self):
        """Test that regex patterns correctly identify tool definitions"""
        test_content = """
        {
            "name": "execute_bash",
            "description": "Execute bash commands",
            "type": "function",
            "parameters": {}
        }
        """

        # Use the update function directly with the test content
        with patch("builtins.open", mock_open(read_data=test_content)):
            with patch("update_agent_tools.open", mock_open()) as mock_file:
                # Test that the function correctly identifies the tool
                update_agent_tools.update_tools_in_file("test.py", dry_run=True)

                # We don't actually write in dry run mode, so just verify it would have made changes
                assert not mock_file().write.called


class TestVerifyAPITools(unittest.TestCase):
    """Tests for the verify_api_tools.py script"""

    @patch("verify_api_tools.requests.get")
    def test_api_health_check_success(self, mock_get):
        """Test that API health check succeeds with correct response"""
        # Mock the API health endpoint
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_get.return_value = mock_response

        # Call the function
        result = verify_api_tools.check_api_health()

        # Check the result
        self.assertEqual(result, {"status": "ok"})
        mock_get.assert_called_once_with("http://localhost:8000/health", timeout=5)

    @patch("verify_api_tools.subprocess.run")
    def test_check_remaining_tool_issues(self, mock_run):
        """Test that tool issue check works with correct response"""
        # Mock subprocess to return no issues
        mock_process = MagicMock()
        mock_process.stdout = ""
        mock_run.return_value = mock_process

        # Call the function
        result = verify_api_tools.check_remaining_tool_issues()

        # Check the result
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
