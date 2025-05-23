"""Claude Agents package."""

# Import core base class
# Import all agent implementations
from .agents import (  # Factory functions
    CodeDebugAgent,
    CriticAgent,
    DependencyManagementAgent,
    ExecutorAgent,
    OptimizedVectorMemoryAgent,
    OrchestratorAgent,
    PlannerAgent,
    TestGeneratorAgent,
    VectorMemoryAgent,
    create_ceo,
    create_executor,
    create_orchestrator,
    create_planner,
    create_summarizer,
    create_test_generator,
)
from .agents.base import Agent

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
    # Factory functions
    "create_ceo",
    "create_planner",
    "create_test_generator",
    "create_summarizer",
    "create_orchestrator",
    "create_executor",
]
