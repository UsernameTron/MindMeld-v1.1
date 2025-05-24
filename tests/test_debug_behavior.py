#!/usr/bin/env python3
"""
Behavior tests for the CodeDebugAgent module.
"""

from unittest.mock import MagicMock

import pytest

from packages.agents.claude_agents.agents.code_debug import CodeDebugAgent
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
      "issues": [
        {
          "type": "syntaxerror",
          "line": 5,
          "description": "Missing colon after if statement",
          "severity": "critical",
          "fix": "Add colon after the condition: if count > 0:"
        },
        {
          "type": "logicalerror",
          "line": 8,
          "description": "Possible division by zero when count is 0",
          "severity": "high",
          "fix": "Add a check to prevent division by zero: if count != 0: average = total / count"
        },
        {
          "type": "runtimeerror",
          "line": 12,
          "description": "Variable 'result' used before assignment",
          "severity": "high",
          "fix": "Initialize result before the conditional: result = None"
        }
      ],
      "fixes": [
        {
          "original": "if count > 0",
          "fixed": "if count > 0:",
          "line": 5,
          "explanation": "Added missing colon after if condition"
        },
        {
          "original": "average = total / count",
          "fixed": "average = total / count if count != 0 else 0",
          "line": 8,
          "explanation": "Added check to prevent division by zero"
        },
        {
          "original": "print(result)",
          "fixed": "result = None\\n    print(result)",
          "line": 12,
          "explanation": "Initialized result before using it"
        }
      ],
      "fixed_code": "def calculate_average(numbers):\\n    total = 0\\n    count = len(numbers)\\n    \\n    if count > 0:\\n        for num in numbers:\\n            total += num\\n        average = total / count if count != 0 else 0\\n        return average\\n    else:\\n        result = None\\n        print(result)\\n        return None",
      "summary": "The code had three main issues: a syntax error (missing colon), a potential division by zero, and a variable used before assignment. All issues have been fixed in the returned code."
    }
    """

    mock_content = []

    # Configure mock tool call response
    mock_tool_call = MagicMock()
    mock_tool_call.name = "debug_code"
    mock_tool_call.output = tool_output_json

    # Set up mock response attributes
    mock_response.content = mock_content
    mock_response.tool_calls = [mock_tool_call]

    # Configure the client to return the mock response
    client.send_message.return_value = mock_response
    client._call_claude = MagicMock(return_value=mock_response)

    return client


@pytest.fixture
def debug_agent(mock_api_client):
    """Create a code debug agent with mock client."""
    return CodeDebugAgent(
        name="debug_agent",
        role="code debugger",
        api_client=mock_api_client,
        temperature=0.1,
    )


def test_debug_agent_fixes_code(debug_agent):
    """Test that debug agent properly identifies and fixes code issues."""
    # Code with bugs to debug
    buggy_code = """def calculate_average(numbers):
    total = 0
    count = len(numbers)

    if count > 0
        for num in numbers:
            total += num
        average = total / count
        return average
    else:
        print(result)
        return None"""

    # Process the debugging
    result = debug_agent.process({"code": buggy_code})

    # Verify result is a dictionary with expected structure
    assert isinstance(result, dict)
    assert "has_errors" in result
    assert "issues" in result

    # Verify that errors were detected
    assert result["has_errors"] == True
    assert len(result["issues"]) > 0

    # Check for specific types of issues that should be detected
    issue_types = [issue["type"] for issue in result["issues"]]
    assert "syntaxerror" in issue_types  # Missing colon should be detected

    # Check that the missing colon issue is specifically detected
    syntax_issues = [
        issue for issue in result["issues"] if issue["type"] == "syntaxerror"
    ]
    assert len(syntax_issues) > 0
    assert any("missing colon" in issue["description"] for issue in syntax_issues)
