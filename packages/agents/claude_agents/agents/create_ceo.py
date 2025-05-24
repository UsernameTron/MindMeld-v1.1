"""Factory function for creating CEO agent."""

from typing import Optional

from ..api.client import ClaudeAPIClient
from .planner import PlannerAgent


def create_ceo(api_client: Optional[ClaudeAPIClient] = None, **kwargs) -> PlannerAgent:
    """
    Create a CEO agent (special planner with executive decision-making capabilities).

    Args:
        api_client: Claude API client instance
        **kwargs: Additional keyword arguments for the agent

    Returns:
        PlannerAgent instance configured as CEO
    """
    return PlannerAgent(
        api_client=api_client, name="ceo", role="Chief Executive Officer", **kwargs
    )
