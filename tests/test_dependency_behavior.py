#!/usr/bin/env python3
"""
Behavior tests for the DependencyManagementAgent module.
"""

from unittest.mock import MagicMock

import pytest

from packages.agents.claude_agents.agents.dependency_management import (
    DependencyManagementAgent,
)
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
      "required_dependencies": [
        {
          "name": "fastapi",
          "version": "^0.100.0",
          "purpose": "Web API framework",
          "is_dev": false
        },
        {
          "name": "sqlalchemy",
          "version": ">=2.0.0",
          "purpose": "SQL ORM",
          "is_dev": false
        },
        {
          "name": "pytest",
          "version": "^7.0.0",
          "purpose": "Testing framework",
          "is_dev": true
        },
        {
          "name": "uvicorn",
          "version": "^0.22.0",
          "purpose": "ASGI server",
          "is_dev": false
        }
      ],
      "missing_dependencies": [
        {
          "name": "sqlalchemy",
          "version": ">=2.0.0",
          "install_priority": "high"
        },
        {
          "name": "uvicorn",
          "version": "^0.22.0",
          "install_priority": "medium"
        }
      ],
      "installation_commands": {
        "pip": "pip install sqlalchemy>=2.0.0 uvicorn~=0.22.0",
        "pipenv": "pipenv install sqlalchemy uvicorn~=0.22.0",
        "poetry": "poetry add sqlalchemy@>=2.0.0 uvicorn@^0.22.0"
      },
      "dev_installation_commands": {
        "pip": "pip install -e .",
        "pipenv": "pipenv install --dev",
        "poetry": "poetry install --with dev"
      }
    }
    """

    mock_content = []

    # Configure mock tool call response
    mock_tool_call = MagicMock()
    mock_tool_call.name = "analyze_dependencies"
    mock_tool_call.output = tool_output_json

    # Set up mock response attributes
    mock_response.content = mock_content
    mock_response.tool_calls = [mock_tool_call]

    # Configure the client to return the mock response
    client.send_message.return_value = mock_response
    client._call_claude = MagicMock(return_value=mock_response)

    return client


@pytest.fixture
def dependency_agent(mock_api_client):
    """Create a dependency management agent with mock client."""
    return DependencyManagementAgent(
        name="dependency_agent",
        role="dependency manager",
        api_client=mock_api_client,
        temperature=0.2,
    )


def test_dependency_analysis(dependency_agent):
    """Test that dependency agent properly analyzes code files and identifies requirements."""
    # Simulate a Python file with imports
    python_code = """
    from fastapi import FastAPI, Depends, HTTPException
    from sqlalchemy import create_engine, Column, Integer, String
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    import uvicorn

    # Test imports
    import pytest

    app = FastAPI()

    Base = declarative_base()

    class User(Base):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)
        name = Column(String)
        email = Column(String)
    """

    # Process the dependency analysis
    result = dependency_agent.process(
        {
            "code": python_code,
            "file_path": "test_app.py",
            "project_path": "/tmp/test_project",
        }
    )

    # Verify result is a dictionary with expected structure
    assert isinstance(result, dict)
    assert "required_dependencies" in result
    assert "missing_dependencies" in result
    assert "installation_commands" in result

    # Verify that the agent detected some dependencies from the code
    assert len(result["required_dependencies"]) > 0

    # Check that common packages are detected
    required_deps = result["required_dependencies"]
    assert "fastapi" in required_deps or "FastAPI" in required_deps
    assert "sqlalchemy" in required_deps or any(
        "sqlalchemy" in dep.lower() for dep in required_deps
    )

    # Verify that missing dependencies are identified
    # (these packages are likely not installed in the test environment)
    assert len(result["missing_dependencies"]) > 0
