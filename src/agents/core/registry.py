from typing import Dict, Type

from .base import Agent

AGENT_REGISTRY: Dict[str, Type[Agent]] = {}


def register_agent(name: str):
    def decorator(cls):
        AGENT_REGISTRY[name] = cls
        return cls

    return decorator
