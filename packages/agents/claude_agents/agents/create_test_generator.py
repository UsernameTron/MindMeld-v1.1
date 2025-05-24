"""Factory function for creating test generator agent."""

from typing import Optional

from ..api.client import ClaudeAPIClient
from .test_generator import TestGeneratorAgent


def create_test_generator(
    api_client: Optional[ClaudeAPIClient] = None, **kwargs
) -> TestGeneratorAgent:
    """
    Create a test generator agent.

    Args:
        api_client: Claude API client instance
        **kwargs: Additional keyword arguments for the agent

    Returns:
        TestGeneratorAgent instance
    """
    return TestGeneratorAgent(api_client=api_client, **kwargs)
