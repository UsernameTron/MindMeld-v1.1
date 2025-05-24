"""Agent registry for Claude Agents."""

REGISTRY = {}


def register_agent(name):
    def decorator(cls):
        REGISTRY[name] = cls
        return cls

    return decorator
