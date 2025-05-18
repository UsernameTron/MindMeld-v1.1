from .core.base import Agent


def create_agent(name: str) -> Agent:
    """
    Factory function to create a new Agent instance.
    """
    return Agent(name)
