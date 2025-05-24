#!/usr/bin/env python3
"""
Behavior tests for the PlannerAgent module.
"""

from unittest.mock import MagicMock

import pytest

from packages.agents.claude_agents.agents.planner import PlannerAgent
from packages.agents.claude_agents.api.client import ClaudeAPIClient


@pytest.fixture
def mock_api_client():
    """Create a mock Claude API client."""
    client = MagicMock(spec=ClaudeAPIClient)

    # Create a structured mock response
    mock_response = MagicMock()

    # Mock the API response with a structured plan
    structured_plan = """{
  "objective": "Deploy LLM with auth and UI",
  "steps": [
    {
      "id": "step_1",
      "description": "Set up authentication service",
      "expected_outcome": "Secure user authentication system"
    },
    {
      "id": "step_2",
      "description": "Configure LLM backend",
      "expected_outcome": "Operational LLM service with API"
    },
    {
      "id": "step_3",
      "description": "Develop frontend UI",
      "expected_outcome": "User-friendly interface for LLM interaction"
    }
  ],
  "estimated_completion_time": "3 days",
  "potential_challenges": [
    "API rate limiting",
    "Token usage optimization",
    "Frontend-backend integration"
  ]
}"""

    mock_content = [
        MagicMock(
            type="text",
            text=f"""```json
{structured_plan}
```""",
        )
    ]

    # Set up mock response attributes
    mock_response.content = mock_content
    mock_response.tool_calls = []

    # Configure the client to return the mock response
    client.send_message.return_value = mock_response
    client._call_claude = MagicMock(return_value=mock_response)

    return client


@pytest.fixture
def planner_agent(mock_api_client):
    """Create a planner agent with mock client."""
    return PlannerAgent(
        api_client=mock_api_client,
        temperature=0.5,
    )


def test_planner_creates_plan(planner_agent):
    """Test that planner generates a structured plan with required fields."""
    result = planner_agent.process("Deploy LLM with auth and UI")

    # Verify result is a dictionary
    assert isinstance(result, dict)

    # Verify it contains the expected structure
    assert "steps" in result
    assert "objective" in result

    # Verify specific content
    assert result["objective"] == "Deploy LLM with auth and UI"
    assert len(result["steps"]) == 3
    assert result["steps"][0]["id"] == "step_1"
    assert result["steps"][1]["description"] == "Configure LLM backend"
    assert "estimated_completion_time" in result
