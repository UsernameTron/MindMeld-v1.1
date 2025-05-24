"""
Centralized agent registry system for MindMeld.

This module provides a mechanism for registering, discovering, and instantiating
agents within the MindMeld ecosystem. It allows for dynamic agent discovery,
capability inspection, and workflow orchestration between multiple agents.
"""

from typing import Any, Callable, Dict, List

from .protocols import AgentProtocol


class AgentRegistry:
    """Centralized registry for agent management and workflow orchestration.

    The AgentRegistry serves as the core component for managing agent instances
    across the MindMeld system. It enables:

    1. Agent registration with capability metadata
    2. Dynamic agent discovery and instantiation
    3. Multi-agent workflow orchestration
    4. Version control and compatibility checking

    This registry is designed to be a singleton that serves as the source of truth
    for all agent-related operations in the system.
    """

    _instance = None

    @classmethod
    def get_instance(cls) -> "AgentRegistry":
        """Get or create the singleton registry instance."""
        if cls._instance is None:
            cls._instance = AgentRegistry()
        return cls._instance

    def __init__(self):
        """Initialize the agent registry with empty collections."""
        if AgentRegistry._instance is not None:
            raise RuntimeError(
                "AgentRegistry is a singleton. Use AgentRegistry.get_instance() instead."
            )

        self.agents = {}
        self.workflows = {}

    def register_agent(
        self,
        name: str,
        factory: Callable[..., AgentProtocol],
        capabilities: Dict[str, Any],
    ) -> None:
        """Register agent with capabilities metadata.

        Args:
            name: Unique identifier for the agent
            factory: Callable that creates an instance of the agent
            capabilities: Dict describing the agent's capabilities

        Raises:
            ValueError: If an agent with the given name is already registered
        """
        if name in self.agents:
            raise ValueError(f"Agent {name!r} is already registered")

        self.agents[name] = {
            "factory": factory,
            "capabilities": capabilities,
            "interface_version": "1.0",
        }

    def unregister_agent(self, name: str) -> None:
        """Remove an agent from the registry.

        Args:
            name: Name of the agent to unregister

        Raises:
            KeyError: If the agent is not registered
        """
        if name not in self.agents:
            raise KeyError(f"Agent {name!r} is not registered")

        del self.agents[name]

    def create_agent(self, name: str, **kwargs) -> AgentProtocol:
        """Create an instance of a registered agent.

        Args:
            name: Name of the agent to instantiate
            **kwargs: Arguments to pass to the agent factory

        Returns:
            An instance of the requested agent

        Raises:
            KeyError: If the agent is not registered
        """
        if name not in self.agents:
            raise KeyError(f"Agent {name!r} is not registered")

        factory = self.agents[name]["factory"]
        return factory(**kwargs)

    def get_agent_capabilities(self, name: str) -> Dict[str, Any]:
        """Get the capabilities of a registered agent.

        Args:
            name: Name of the agent

        Returns:
            Dict containing the agent's capabilities

        Raises:
            KeyError: If the agent is not registered
        """
        if name not in self.agents:
            raise KeyError(f"Agent {name!r} is not registered")

        return self.agents[name]["capabilities"]

    def list_agents(self) -> List[str]:
        """Get a list of all registered agent names."""
        return list(self.agents.keys())

    def create_workflow(self, workflow_name: str, agent_sequence: List[str]) -> None:
        """Create multi-agent workflow definitions.

        A workflow represents a sequence of agents that process data in order,
        with each agent receiving the output of the previous agent as input.

        Args:
            workflow_name: Unique identifier for the workflow
            agent_sequence: Ordered list of agent names to execute in sequence

        Raises:
            ValueError: If a workflow with the given name already exists
            KeyError: If any agent in the sequence is not registered
        """
        if workflow_name in self.workflows:
            raise ValueError(f"Workflow {workflow_name!r} already exists")

        # Verify all agents exist
        for agent_name in agent_sequence:
            if agent_name not in self.agents:
                raise KeyError(
                    f"Cannot create workflow - agent {agent_name!r} is not registered"
                )

        self.workflows[workflow_name] = agent_sequence

    def execute_workflow(
        self, workflow_name: str, input_data: Dict[str, Any], **kwargs
    ) -> Dict[str, Any]:
        """Execute a multi-agent workflow with the given input data.

        Args:
            workflow_name: Name of the workflow to execute
            input_data: Initial input data for the workflow
            **kwargs: Additional arguments to pass to agent factories

        Returns:
            The output from the final agent in the workflow

        Raises:
            KeyError: If the workflow is not registered
            RuntimeError: If any agent in the workflow raises an exception
        """
        if workflow_name not in self.workflows:
            raise KeyError(f"Workflow {workflow_name!r} is not registered")

        agent_sequence = self.workflows[workflow_name]
        current_data = input_data

        workflow_results = {"steps": [], "success": True, "final_output": None}

        # Execute each agent in sequence
        for agent_name in agent_sequence:
            try:
                # Create a fresh agent instance for each step
                agent = self.create_agent(agent_name, **kwargs)

                # Process data through the agent
                step_result = agent.process(current_data)

                # Record step results
                workflow_results["steps"].append(
                    {
                        "agent": agent_name,
                        "success": step_result.get("success", False),
                        "message": step_result.get("message", ""),
                    }
                )

                # Update current_data for the next agent
                current_data = step_result

                # If any step fails, mark the workflow as failed
                if not step_result.get("success", False):
                    workflow_results["success"] = False
                    workflow_results["error"] = step_result.get(
                        "message", "Step failed"
                    )
                    break

            except Exception as e:
                workflow_results["success"] = False
                workflow_results["error"] = str(e)
                raise RuntimeError(
                    f"Workflow {workflow_name!r} failed at step {agent_name!r}: {str(e)}"
                ) from e

        workflow_results["final_output"] = current_data
        return workflow_results
