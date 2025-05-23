#!/usr/bin/env python3
"""
Behavior tests for the CriticAgent module.
"""

from unittest.mock import MagicMock, patch

import pytest

from packages.agents.claude_agents.agents.critic import CriticAgent
from packages.agents.claude_agents.api.client import ClaudeAPIClient


@pytest.fixture
def mock_api_client():
    """Create a mock Claude API client."""
    client = MagicMock(spec=ClaudeAPIClient)

    # Create a structured mock response
    mock_response = MagicMock()

    # Mock the API response using the tool function output format
    tool_output_json = """
    {
      "quality_score": 7.5,
      "correctness_score": 8.0,
      "completeness_score": 7.0,
      "issues": [
        {
          "severity": "major",
          "description": "The authentication logic lacks proper error handling for invalid tokens",
          "location": "login_handler function",
          "recommendation": "Add try/except block to catch JWT validation errors"
        },
        {
          "severity": "minor",
          "description": "Missing type hints in several function parameters",
          "location": "create_user, update_profile functions",
          "recommendation": "Add Python type annotations for better code clarity"
        }
      ],
      "recommendations": [
        {
          "priority": "high",
          "description": "Implement proper token validation with exception handling",
          "benefit": "Prevents security vulnerabilities and improves error reporting"
        },
        {
          "priority": "medium",
          "description": "Add comprehensive docstrings to all public functions",
          "benefit": "Improves code maintainability and developer onboarding"
        }
      ],
      "summary": "The code is generally well-structured but has some security concerns in the authentication implementation and could benefit from better documentation."
    }
    """

    mock_content = []

    # Configure mock tool call response
    mock_tool_call = MagicMock()
    mock_tool_call.function = MagicMock()
    mock_tool_call.function.name = "evaluate_output"
    mock_tool_call.function.arguments = tool_output_json

    # Set up mock response attributes
    mock_response.content = mock_content
    mock_response.tool_calls = [mock_tool_call]

    # Configure the client to return the mock response
    client.send_message.return_value = mock_response
    client._call_claude = MagicMock(return_value=mock_response)

    return client


@pytest.fixture
def critic_agent(mock_api_client):
    """Create a critic agent with mock client."""
    return CriticAgent(
        api_client=mock_api_client,
        temperature=0.3,
    )


def test_critic_evaluates_output(critic_agent):
    """Test that critic agent properly evaluates code and provides feedback."""
    # Code to evaluate with an authentication implementation
    code_to_evaluate = """
    def login_handler(request):
        username = request.json.get('username')
        password = request.json.get('password')

        if not username or not password:
            return {'error': 'Missing credentials'}, 400

        user = authenticate_user(username, password)
        if not user:
            return {'error': 'Invalid credentials'}, 401

        token = create_jwt_token(user.id)
        return {'token': token}, 200
    """

    # Requirements to evaluate against
    requirements = {
        "security": "Must implement proper authentication",
        "maintainability": "Code should be well-documented",
        "performance": "Should handle requests efficiently",
    }

    # Process the evaluation
    result = critic_agent.process(code_to_evaluate, requirements)

    # Verify result is a dictionary with expected structure
    assert isinstance(result, dict)
    assert "quality_score" in result
    assert "issues" in result
    assert "recommendations" in result

    # Verify specific content
    assert result["quality_score"] == 7.5
    assert result["correctness_score"] == 8.0
    assert len(result["issues"]) == 2
    assert result["issues"][0]["severity"] == "major"
    assert "authentication logic" in result["issues"][0]["description"]

    # Verify recommendations
    assert len(result["recommendations"]) == 2
    assert any(
        "token validation" in rec["description"] for rec in result["recommendations"]
    )
