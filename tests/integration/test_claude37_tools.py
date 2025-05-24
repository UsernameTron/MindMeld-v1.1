#!/usr/bin/env python3
"""
Integration test to verify Claude 3.7 API tool compatibility
"""

import os
import unittest

import requests

# Define test constants
API_URL = "http://localhost:8000"
TEST_AGENT = "planner"  # Use the planner agent which has updated tools


class TestClaude37ToolCompatibility(unittest.TestCase):
    """Integration tests for Claude 3.7 API tool compatibility"""

    def setUp(self):
        """Set up common test fixtures"""
        # Check if the API is running
        try:
            response = requests.get(f"{API_URL}/health", timeout=2)
            self.api_available = response.status_code == 200
        except Exception:
            self.api_available = False

    def test_get_agent_definition(self):
        """Test that agent definitions have the correct tool types"""
        # Skip if API is not available
        if not self.api_available:
            self.skipTest("API is not available")

        response = requests.get(f"{API_URL}/agents/definitions/{TEST_AGENT}")
        self.assertEqual(response.status_code, 200)

        agent_def = response.json()

        # Check that the agent definition has tools
        self.assertIn("tools", agent_def)
        self.assertTrue(len(agent_def["tools"]) > 0)

        # Ensure no tool has "type": "function"
        for tool in agent_def["tools"]:
            self.assertIn("type", tool)
            self.assertNotEqual(tool["type"], "function")

            # Check specific tools have the right type
            if tool.get("name") == "execute_bash":
                self.assertEqual(tool["type"], "bash_20250124")
            elif tool.get("name") == "search_web":
                self.assertEqual(tool["type"], "web_search_20250305")

    @unittest.skipIf(not os.environ.get("RUN_LIVE_TESTS"), "Skipping live API test")
    def test_agent_execution(self):
        """Test that an agent can be executed with the updated tools"""
        # Skip if API is not available
        if not self.api_available:
            self.skipTest("API is not available")

        # Run a simple agent with a prompt that shouldn't need tools
        response = requests.post(
            f"{API_URL}/agents/run",
            json={
                "agent_name": TEST_AGENT,
                "prompt": "What is 2+2?",
                "max_tokens": 100,
            },
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()

        # Ensure we got a successful response
        self.assertNotIn("error", result)
        self.assertIn("response", result)


if __name__ == "__main__":
    unittest.main()
