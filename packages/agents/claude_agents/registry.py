"""
Agent registry for keeping track of available agent implementations.
"""

# Registry of agent implementations
AGENT_REGISTRY = {}


def register_agent(name):
    """
    Decorator to register an agent implementation.

    Args:
        name: A unique name for the agent

    Returns:
        The decorator function
    """

    def decorator(cls):
        AGENT_REGISTRY[name] = cls
        return cls

    return decorator
