"""
Simple test for one factory function to ensure our compatibility layer works.
"""

import os
import sys
import unittest

# Add the parent directory to the path so we can import from packages
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import directly from the module
from packages.agents.advanced_reasoning.agents import TestGeneratorAgent


class TestAgentClass(unittest.TestCase):
    """Test agent classes directly."""

    def test_test_generator_agent(self):
        """Test that TestGeneratorAgent can be instantiated."""
        from packages.agents.claude_agents.api.mock_client import MockClaudeAPIClient

        api_client = MockClaudeAPIClient()

        agent = TestGeneratorAgent(
            name="test_gen", role="Test Generator", api_client=api_client
        )

        self.assertEqual(agent.name, "test_gen")
        self.assertEqual(agent.role, "Test Generator")
        self.assertIsNotNone(agent.api_client)


if __name__ == "__main__":
    unittest.main()
