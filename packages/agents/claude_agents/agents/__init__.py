"""Agent implementations for Claude Agents."""

# Core base class
from .base import Agent
from .code_debug import CodeDebugAgent

# Factory functions (keep existing pattern)
from .create_ceo import create_ceo
from .create_executor import create_executor
from .create_orchestrator import create_orchestrator
from .create_planner import create_planner
from .create_summarizer import create_summarizer
from .create_test_generator import create_test_generator
from .critic import CriticAgent
from .dependency_management import DependencyManagementAgent
from .executor import ExecutorAgent
from .optimized_vector_memory import OptimizedVectorMemoryAgent
from .orchestrator import OrchestratorAgent

# Core reasoning agents
from .planner import PlannerAgent

# Tool agents
from .test_generator import TestGeneratorAgent

# Memory agents
from .vector_memory import VectorMemoryAgent

__all__ = [
    "Agent",
    "PlannerAgent",
    "CriticAgent",
    "ExecutorAgent",
    "OrchestratorAgent",
    "TestGeneratorAgent",
    "CodeDebugAgent",
    "DependencyManagementAgent",
    "VectorMemoryAgent",
    "OptimizedVectorMemoryAgent",
    "create_ceo",
    "create_planner",
    "create_test_generator",
    "create_summarizer",
    "create_orchestrator",
    "create_executor",
]
