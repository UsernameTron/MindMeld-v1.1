"""
Tests for the agent registry system.

This module contains unit tests for the AgentRegistry class to ensure
it correctly handles agent registration, workflow creation, and execution.
"""

from typing import Any, Dict

import pytest

from packages.agents.base.registry import AgentRegistry


class MockAgent:
    """A simple mock agent for testing the registry."""

    def __init__(self, name="MockAgent", response=None):
        self.name = name
        self.response = response or {"success": True, "message": "Processing complete"}

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data and return a mock response."""
        result = self.response.copy()
        # Add the input data to the result for testing data flow
        result["input_received"] = input_data
        return result

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Mock input validation always returns True."""
        return True

    def get_capabilities(self) -> Dict[str, Any]:
        """Return mock capabilities."""
        return {
            "name": self.name,
            "description": "A mock agent for testing",
            "version": "1.0.0",
        }


def test_registry_singleton():
    """Test that the registry behaves as a singleton."""
    registry1 = AgentRegistry.get_instance()
    registry2 = AgentRegistry.get_instance()

    assert registry1 is registry2

    # Ensure direct instantiation raises an error
    with pytest.raises(RuntimeError):
        AgentRegistry()


def test_register_agent():
    """Test agent registration and retrieval."""
    registry = AgentRegistry.get_instance()

    # Clear any existing registrations for clean testing
    registry.agents = {}

    # Define a factory function
    def mock_factory(**kwargs):
        return MockAgent(**kwargs)

    # Register the agent
    registry.register_agent("mock_agent", mock_factory, {"description": "A test agent"})

    # Check registration
    assert "mock_agent" in registry.agents
    assert registry.agents["mock_agent"]["factory"] == mock_factory
    assert (
        registry.agents["mock_agent"]["capabilities"]["description"] == "A test agent"
    )

    # Test duplicate registration
    with pytest.raises(ValueError):
        registry.register_agent("mock_agent", mock_factory, {})


def test_create_agent():
    """Test agent instantiation from registry."""
    registry = AgentRegistry.get_instance()

    # Clear any existing registrations for clean testing
    registry.agents = {}

    # Register an agent with a factory that handles name mapping
    registry.register_agent(
        "test_agent",
        lambda **kwargs: MockAgent(name=kwargs.get("agent_name", "default")),
        {"description": "Test agent"},
    )

    # Create an instance
    agent = registry.create_agent("test_agent", agent_name="CustomName")

    # Verify the instance
    assert isinstance(agent, MockAgent)
    assert agent.name == "CustomName"

    # Test creating non-existent agent
    with pytest.raises(KeyError):
        registry.create_agent("nonexistent_agent")


def test_workflow_creation():
    """Test creating and validating workflows."""
    registry = AgentRegistry.get_instance()

    # Clear existing registrations
    registry.agents = {}
    registry.workflows = {}

    # Register test agents
    for name in ["agent1", "agent2", "agent3"]:
        registry.register_agent(
            name,
            lambda **kwargs: MockAgent(name=kwargs.get("name", "default")),
            {"description": f"Test {name}"},
        )

    # Create a workflow
    registry.create_workflow("test_workflow", ["agent1", "agent2", "agent3"])

    # Verify workflow
    assert "test_workflow" in registry.workflows
    assert registry.workflows["test_workflow"] == ["agent1", "agent2", "agent3"]

    # Test duplicate workflow
    with pytest.raises(ValueError):
        registry.create_workflow("test_workflow", ["agent1"])

    # Test workflow with invalid agent
    with pytest.raises(KeyError):
        registry.create_workflow("invalid_workflow", ["agent1", "nonexistent"])


def test_workflow_execution():
    """Test executing a workflow with multiple agents."""
    registry = AgentRegistry.get_instance()

    # Clear existing registrations
    registry.agents = {}
    registry.workflows = {}

    # Register test agents with different responses
    registry.register_agent(
        "first_agent",
        lambda **kwargs: MockAgent(response={"success": True, "data": "first result"}),
        {"description": "First test agent"},
    )

    registry.register_agent(
        "second_agent",
        lambda **kwargs: MockAgent(response={"success": True, "data": "second result"}),
        {"description": "Second test agent"},
    )

    # Create a workflow
    registry.create_workflow("data_pipeline", ["first_agent", "second_agent"])

    # Execute the workflow
    input_data = {"query": "test query"}
    result = registry.execute_workflow("data_pipeline", input_data)

    # Verify results
    assert result["success"] is True
    assert len(result["steps"]) == 2
    assert result["steps"][0]["agent"] == "first_agent"
    assert result["steps"][1]["agent"] == "second_agent"

    # Verify data passed between agents
    assert result["final_output"]["input_received"]["data"] == "first result"

    # Test executing non-existent workflow
    with pytest.raises(KeyError):
        registry.execute_workflow("nonexistent_workflow", {})
