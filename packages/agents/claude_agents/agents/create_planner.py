"""Factory function for creating planner agent."""

from typing import Optional

from ..api.client import ClaudeAPIClient
from .planner import PlannerAgent


def create_planner(
    api_client: Optional[ClaudeAPIClient] = None, **kwargs
) -> PlannerAgent:
    """
    Create a planner agent.

    Args:
        api_client: Claude API client instance
        **kwargs: Additional keyword arguments for the agent

    Returns:
        PlannerAgent instance
    """
    # Handle api_client if None
    if api_client is None:
        from ..api.client import ClaudeAPIClient

        api_client = ClaudeAPIClient()

    return PlannerAgent(api_client=api_client, **kwargs)
