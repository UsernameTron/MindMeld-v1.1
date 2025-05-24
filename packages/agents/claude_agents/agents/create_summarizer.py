"""Factory function for creating summarizer agent."""

from typing import Optional

from ..api.client import ClaudeAPIClient
from .executor import ExecutorAgent


def create_summarizer(
    api_client: Optional[ClaudeAPIClient] = None, **kwargs
) -> ExecutorAgent:
    """
    Create a summarizer agent (specialized executor for summarizing content).

    Args:
        api_client: Claude API client instance
        **kwargs: Additional keyword arguments for the agent

    Returns:
        ExecutorAgent instance configured as summarizer
    """
    # Handle api_client if None
    if api_client is None:
        from ..api.client import ClaudeAPIClient

        api_client = ClaudeAPIClient()

    return ExecutorAgent(api_client=api_client, name="Content Summarizer", **kwargs)
