#!/usr/bin/env python3
"""
Simplified analysis script for the MindMeld codebase.
This script demonstrates using the agent system to analyze itself
with a more focused scope for quicker results.
"""

import json
import logging
import os
import time

from src.agents.core.registry import AgentRegistry
from src.agents.implementations.code_debug import CodeDebugAgent
from src.agents.implementations.dependency_management import DependencyManagementAgent
from src.agents.memory.optimized_vector_memory import OptimizedVectorMemoryAgent
from src.ai.client import LLMClientFactory

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_agent_system():
    """Set up a minimal agent system for quick analysis"""
    # Create LLM client
    llm_client = LLMClientFactory.create_client(
        client_type="ollama", model="codellama"  # Adjust to a model you have in Ollama
    )

    # Create data directories
    os.makedirs("./data/storage/vector_memory", exist_ok=True)
    os.makedirs("./data/outputs/quick_analysis", exist_ok=True)

    # Create agent registry
    registry = AgentRegistry()

    # Create minimal set of agents
    vector_memory = OptimizedVectorMemoryAgent(
        storage_path="./data/storage/vector_memory",
        llm_client=llm_client,
        similarity_threshold=0.6,
    )

    code_debugger = CodeDebugAgent(llm_client=llm_client)

    dependency_manager = DependencyManagementAgent(llm_client=llm_client)

    # Register agents
    registry.register(vector_memory)
    registry.register(code_debugger)
    registry.register(dependency_manager)

    logger.info(
        f"Quick analysis agent system initialized with {len(registry.list_agents())} agents"
    )

    return registry


def quick_analyze():
    """Run a quick analysis on selected core components"""
    # Set up agent system
    registry = setup_agent_system()

    # Set up paths
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    output_dir = os.path.join(project_root, "data", "outputs", "quick_analysis")
    os.makedirs(output_dir, exist_ok=True)

    # Key files to analyze
    core_files = [
        os.path.join(project_root, "src", "agents", "core", "base.py"),
        os.path.join(project_root, "src", "agents", "core", "registry.py"),
        os.path.join(project_root, "src", "ai", "client.py"),
    ]

    results = {}

    # Analyze each file for issues
    for file_path in core_files:
        rel_path = os.path.relpath(file_path, project_root)
        logger.info(f"Quick analyzing file: {rel_path}")

        try:
            with open(file_path, "r") as f:
                file_content = f.read()

            # Use code debug agent to detect issues
            debug_result = registry.dispatch(
                "code_debug",
                {
                    "code": file_content,
                    "language": "python",
                    "filename": os.path.basename(file_path),
                },
            )

            # Save result
            results[rel_path] = debug_result

            # Store in vector memory for potential reference
            registry.dispatch(
                "vector_memory",
                {
                    "command": "add",
                    "content": f"Code analysis of {rel_path}: {json.dumps(debug_result)}",
                    "metadata": {"type": "code_analysis", "file_path": rel_path},
                },
            )
        except Exception as e:
            logger.error(f"Error analyzing {rel_path}: {str(e)}")

    # Perform a dependency analysis
    try:
        dependency_analysis = registry.dispatch(
            "dependency_management",
            {"command": "analyze_project", "project_root": project_root},
        )

        # Save dependency analysis
        results["dependency_analysis"] = dependency_analysis
    except Exception as e:
        logger.error(f"Error in dependency analysis: {str(e)}")

    # Save consolidated results
    with open(os.path.join(output_dir, "quick_analysis_results.json"), "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    print("\n" + "=" * 80)
    print("MINDMELD QUICK ANALYSIS SUMMARY")
    print("=" * 80)

    for file_path, result in results.items():
        if file_path == "dependency_analysis":
            continue

        if result.get("has_errors", False):
            issue_count = len(result.get("issues", []))
            print(f"\n{file_path}: {issue_count} potential issues found")
        else:
            print(f"\n{file_path}: No significant issues detected")

    # Dependency summary
    if "dependency_analysis" in results:
        dep_result = results["dependency_analysis"]
        print("\nDependency Analysis:")
        print(
            f"- Missing dependencies: {len(dep_result.get('missing_dependencies', []))}"
        )
        print(f"- Version conflicts: {len(dep_result.get('version_conflicts', []))}")
        print(f"- Security concerns: {len(dep_result.get('security_concerns', []))}")

    print("\nFull analysis results available in:", output_dir)
    print("=" * 80 + "\n")

    return output_dir


if __name__ == "__main__":
    start_time = time.time()
    output_dir = quick_analyze()
    elapsed_time = time.time() - start_time
    logger.info(f"Quick analysis completed in {elapsed_time:.2f} seconds")

    if output_dir:
        print(
            f"\nAnalysis results are available in: {output_dir}/quick_analysis_results.json"
        )
