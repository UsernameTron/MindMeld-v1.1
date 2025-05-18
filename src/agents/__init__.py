"""
Package: agents
"""

__version__ = "0.1.0"

# Import important classes to expose at the package level
from .core.base import Agent
from .factory import create_agent

__all__ = ["Agent", "create_agent"]

# This file marks the agents package as a Python package.
