"""Tests for the CodeDebugAgent implementation."""

from packages.agents.claude_agents.agents.code_debug import CodeDebugAgent
from packages.agents.claude_agents.api.mock_client import MockClaudeAPIClient


def test_code_debug_agent_initialization():
    """Test that the CodeDebugAgent can be initialized."""
    api_client = MockClaudeAPIClient()
    agent = CodeDebugAgent(
        name="code_debug", role="code debugger", api_client=api_client
    )
    assert agent is not None


def test_check_syntax_with_missing_colon():
    """Test that the agent can detect missing colons in code."""
    api_client = MockClaudeAPIClient()
    agent = CodeDebugAgent(
        name="code_debug", role="code debugger", api_client=api_client
    )
    code = """def test_function()
    print("Hello, world!")
"""
    issues = agent._check_syntax(code)
    assert len(issues) > 0
    assert any(
        issue["type"] == "syntaxerror" and "missing colon" in issue["description"]
        for issue in issues
    )


def test_check_logical_errors_division_by_zero():
    """Test that the agent can detect potential division by zero."""
    api_client = MockClaudeAPIClient()
    agent = CodeDebugAgent(
        name="code_debug", role="code debugger", api_client=api_client
    )
    code = """def divide(a, b):
    return a / b

result = divide(10, 0)
"""
    issues = agent._check_logical_errors(code)
    assert len(issues) > 0
    assert any(
        issue["type"] == "logicalerror" and "division by zero" in issue["description"]
        for issue in issues
    )


def test_check_performance_nested_loops():
    """Test that the agent can detect nested loops that might cause performance issues."""
    api_client = MockClaudeAPIClient()
    agent = CodeDebugAgent(
        name="code_debug", role="code debugger", api_client=api_client
    )
    code = """def process_data(items):
    for item in items:
        for sub_item in item:
            print(sub_item)
"""
    issues = agent._check_performance(code)
    assert len(issues) > 0
    assert any(
        issue["type"] == "performance" and "o(n²)" in issue["description"]
        for issue in issues
    )


def test_check_security_issues():
    """Test that the agent can detect security vulnerabilities."""
    api_client = MockClaudeAPIClient()
    agent = CodeDebugAgent(
        name="code_debug", role="code debugger", api_client=api_client
    )
    code = """import subprocess

def run_command(cmd):
    subprocess.call(cmd, shell=True)  # Security risk
"""
    issues = agent._check_security(code)
    assert len(issues) > 0
    assert any(
        issue["type"] == "security" and "command injection" in issue["description"]
        for issue in issues
    )


def test_full_process_with_multiple_issues():
    """Test the full process method with code that has multiple issues."""
    api_client = MockClaudeAPIClient()
    agent = CodeDebugAgent(
        name="code_debug", role="code debugger", api_client=api_client
    )
    code = """def insecure_function(cmd)
    subprocess.call(cmd, shell=True)

def divide_values(a, b):
    return a / b

def process_data(items):
    for item in items:
        for sub_item in item:
            print(sub_item)
"""
    result = agent.process({"code": code})
    assert result["has_errors"] is True
    assert len(result["issues"]) > 0

    # Check that we have different types of issues
    issue_types = {issue["type"] for issue in result["issues"]}
    assert len(issue_types) > 1  # Should have at least 2 different types of issues
