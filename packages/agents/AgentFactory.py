from .advanced_reasoning.agents import create_ceo, create_executor, create_summarizer, create_test_generator, create_dependency_agent
from .advanced_reasoning.agents import Agent, TestGeneratorAgent, DependencyAgent, CodeAnalyzerAgent, CodeDebuggerAgent, CodeRepairAgent, PerformanceProfilerAgent, OptimizationSuggesterAgent, BenchmarkingTool, IntegratedCodebaseOptimizer, pipeline_coordinator, CodeEmbeddingIndex, SemanticCodeSearch

# Input type definitions
AGENT_INPUT_TYPES = {
    "TestGeneratorAgent": "file",
    "DependencyAgent": "directory",
    "CodeAnalyzerAgent": "directory",
    "CodeDebuggerAgent": "file",
    "CodeRepairAgent": "file",
    "CodeEmbeddingIndex": "directory",
    "SemanticCodeSearch": "directory",
    "PerformanceProfilerAgent": "file",
    "OptimizationSuggesterAgent": "file",
    "BenchmarkingTool": "directory",
    "IntegratedCodebaseOptimizer": "directory",
    "summarizer": "integer",
    "ceo": "string",
    "executor": "string",
    "dependency_agent": "directory",
    "test_generator": "file",
}

# Central registry
def get_registry():
    registry = {}
    registry.update({
        "Agent": Agent,
        "TestGeneratorAgent": TestGeneratorAgent,
        "DependencyAgent": DependencyAgent,
        "ceo": create_ceo,
        "executor": create_executor,
        "summarizer": create_summarizer,
        "test_generator": create_test_generator,
        "dependency_agent": create_dependency_agent,
        "CodeAnalyzerAgent": CodeAnalyzerAgent,
        "CodeDebuggerAgent": CodeDebuggerAgent,
        "CodeRepairAgent": CodeRepairAgent,
        "CodeEmbeddingIndex": CodeEmbeddingIndex,
        "SemanticCodeSearch": SemanticCodeSearch,
        "PerformanceProfilerAgent": PerformanceProfilerAgent,
        "OptimizationSuggesterAgent": OptimizationSuggesterAgent,
        "BenchmarkingTool": BenchmarkingTool,
        "IntegratedCodebaseOptimizer": IntegratedCodebaseOptimizer,
        "pipeline_coordinator": pipeline_coordinator,
    })
    return registry

AGENT_REGISTRY = get_registry()
