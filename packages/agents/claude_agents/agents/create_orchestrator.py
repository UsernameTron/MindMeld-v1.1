"""Factory function for creating orchestrator agent."""

from typing import Optional

from ..api.client import ClaudeAPIClient
from .orchestrator import OrchestratorAgent


def create_orchestrator(
    api_client: Optional[ClaudeAPIClient] = None, **kwargs
) -> OrchestratorAgent:
    """
    Create an orchestrator agent.

    Args:
        api_client: Claude API client instance
        **kwargs: Additional keyword arguments for the agent

    Returns:
        OrchestratorAgent instance
    """
    return OrchestratorAgent(api_client=api_client, **kwargs)
