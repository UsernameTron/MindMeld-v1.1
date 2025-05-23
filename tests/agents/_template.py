"""Template for agent tests."""

import pytest

from packages.agents.claude_agents.agents.base import Agent
from packages.agents.claude_agents.api.mock_client import MockClaudeAPIClient


class TestAgentTemplate:
    """Template test class for agents."""

    @pytest.fixture
    def mock_client(self):
        return MockClaudeAPIClient()

    @pytest.fixture
    def agent(self, mock_client):
        # Override in specific test files
        raise NotImplementedError("Override in specific test file")

    def test_agent_initialization(self, agent):
        assert isinstance(agent, Agent)
        assert agent.name is not None
        assert agent.role is not None

    def test_agent_process_method_exists(self, agent):
        assert hasattr(agent, "process")
        assert callable(agent.process)
