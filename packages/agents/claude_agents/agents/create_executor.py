"""Factory function for creating executor agent."""

from typing import Optional

from ..api.client import ClaudeAPIClient
from .executor import ExecutorAgent


def create_executor(
    api_client: Optional[ClaudeAPIClient] = None, **kwargs
) -> ExecutorAgent:
    """
    Create an executor agent.

    Args:
        api_client: Claude API client instance
        **kwargs: Additional keyword arguments for the agent

    Returns:
        ExecutorAgent instance
    """
    return ExecutorAgent(api_client=api_client, **kwargs)
