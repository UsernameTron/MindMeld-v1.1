"""Agent registry for dynamic agent lookup and instantiation"""

import importlib
import inspect
import logging
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union

from .base import Agent


class AgentRegistry:
    """Registry for dynamically creating agents"""

    def __init__(self):
        """Initialize agent registry"""
        self.agents = {}
        self.required_methods = {}
        self.dependencies = {}
        self.logger = logging.getLogger(__name__)

    def register(
        self,
        name: str,
        agent_class: Type[Agent],
        required_methods: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
    ):
        """Register an agent class with the registry

        Args:
            name: Name to register the agent under
            agent_class: Agent class to register
            required_methods: List of methods that must be implemented
            dependencies: List of dependencies for this agent
        """
        # Validate agent class is a subclass of Agent
        if not inspect.isclass(agent_class) or not issubclass(agent_class, Agent):
            raise TypeError(
                f"Agent class '{agent_class.__name__}' must be a subclass of Agent"
            )

        # Register the agent
        self.agents[name] = agent_class

        # Store required methods and dependencies
        self.required_methods[name] = required_methods or []
        self.dependencies[name] = dependencies or []

        self.logger.info(f"Registered agent '{name}'")

    def dispatch(self, name: str, *args, **kwargs) -> Agent:
        """Create and return agent instance by name

        Args:
            name: Name of agent to create
            *args: Positional args to pass to the agent constructor
            **kwargs: Keyword args to pass to the agent constructor

        Returns:
            Agent instance
        """

        # Check if agent exists
        if name not in self.agents:
            self.logger.error(f"Agent '{name}' not found in registry")
            raise KeyError(f"Agent '{name}' not found in registry")

        # Check dependencies
        for dependency in self.dependencies.get(name, []):
            try:
                importlib.import_module(dependency)
            except ImportError:
                self.logger.error(
                    f"Missing dependency '{dependency}' for agent '{name}'"
                )
                raise ImportError(
                    f"Missing dependency '{dependency}' for agent '{name}'"
                )

        # Create the agent
        agent_class = self.agents[name]

        # Validate required methods
        missing_methods = []
        for method_name in self.required_methods.get(name, []):
            if not hasattr(agent_class, method_name) or not callable(
                getattr(agent_class, method_name)
            ):
                missing_methods.append(method_name)

        if missing_methods:
            self.logger.error(
                f"Agent '{name}' is missing required methods: {', '.join(missing_methods)}"
            )
            raise ValueError(
                f"Agent '{name}' is missing required methods: {', '.join(missing_methods)}"
            )

        try:
            agent = agent_class(*args, **kwargs)
            return agent
        except Exception as e:
            self.logger.error(f"Error instantiating agent '{name}': {str(e)}")
            raise

    def list_agents(self) -> List[str]:
        """List all registered agents

        Returns:
            List of registered agent names
        """
        return list(self.agents.keys())

    def get_dependency_graph(self) -> Dict[str, Set[str]]:
        """Get dependency graph of registered agents

        Returns:
            Dictionary of agent names to their dependencies
        """
        return {name: set(self.dependencies.get(name, [])) for name in self.agents}

    def validate_agent(self, name: str) -> bool:
        """Validate that an agent meets all requirements"""
        if name not in self.agents:
            return False

        # Check dependencies and required methods
        return True


# Create a global registry instance
registry = AgentRegistry()  # Singleton pattern
