#!/usr/bin/env python3
"""
Comprehensive analysis script for the MindMeld codebase.
This script demonstrates using the agent system to analyze itself.
"""

import glob
import json
import logging
import os
import time

from src.agents.core.registry import AgentRegistry
from src.agents.implementations.code_debug import CodeDebugAgent
from src.agents.implementations.code_organizer import CodeOrganizerAgent
from src.agents.implementations.dependency_management import DependencyManagementAgent
from src.agents.implementations.planner import PlannerAgent
from src.agents.implementations.test_generator import TestGeneratorAgent
from src.agents.memory.optimized_vector_memory import OptimizedVectorMemoryAgent
from src.ai.client import LLMClientFactory

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_agent_system():
    """Set up the complete agent system with all specialized agents"""
    # Create LLM client
    llm_client = LLMClientFactory.create_client(
        client_type="ollama", model="codellama"  # Adjust to a model you have in Ollama
    )

    # Create data directories
    os.makedirs("./data/storage/vector_memory", exist_ok=True)
    os.makedirs("./data/outputs/analysis", exist_ok=True)

    # Create agent registry
    registry = AgentRegistry()

    # Create agents
    vector_memory = OptimizedVectorMemoryAgent(
        storage_path="./data/storage/vector_memory",
        llm_client=llm_client,
        similarity_threshold=0.6,  # Lower threshold for more results
    )

    code_organizer = CodeOrganizerAgent(
        llm_client=llm_client, output_dir="./data/outputs/analysis"
    )

    test_generator = TestGeneratorAgent(
        llm_client=llm_client, output_dir="./data/outputs/analysis"
    )

    code_debugger = CodeDebugAgent(llm_client=llm_client)

    dependency_manager = DependencyManagementAgent(llm_client=llm_client)

    # Register all agents
    registry.register(vector_memory)
    registry.register(code_organizer)
    registry.register(test_generator)
    registry.register(code_debugger)
    registry.register(dependency_manager)

    # Create and register planner agent
    planner = PlannerAgent(registry=registry, llm_client=llm_client)
    registry.register(planner)

    logger.info(f"Agent system initialized with {len(registry.list_agents())} agents")

    return registry, planner


def collect_files(directory, extensions=None):
    """Collect all relevant files from directory"""
    extensions = extensions or [".py"]

    all_files = []
    for ext in extensions:
        pattern = os.path.join(directory, f"**/*{ext}")
        all_files.extend(glob.glob(pattern, recursive=True))

    return all_files


def analyze_codebase():
    """Run a full analysis on the MindMeld codebase"""
    # Set up agent system
    registry, planner = setup_agent_system()

    # Find all Python files in the src directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    src_dir = os.path.join(project_root, "src")

    if not os.path.exists(src_dir):
        logger.error(f"Source directory not found: {src_dir}")
        return

    python_files = collect_files(src_dir, extensions=[".py"])
    logger.info(f"Found {len(python_files)} Python files to analyze")

    # Create output directory for analysis results
    output_dir = os.path.join(project_root, "data", "outputs", "analysis")
    os.makedirs(output_dir, exist_ok=True)

    # Start with a high-level architecture analysis plan
    architecture_plan = registry.dispatch(
        "planner",
        {
            "command": "create_plan",
            "description": "Analyze the MindMeld codebase architecture and identify key components and their relationships",
            "context": {
                "project_root": project_root,
                "file_count": len(python_files),
                "directories": set(os.path.dirname(f) for f in python_files),
            },
        },
    )

    if architecture_plan["status"] == "success":
        plan_id = architecture_plan["plan_id"]
        logger.info(f"Created architecture analysis plan: {plan_id}")

        # Execute the architecture analysis plan
        arch_result = registry.dispatch(
            "planner", {"command": "execute_plan", "plan_id": plan_id}
        )

        # Save the architecture analysis results
        with open(os.path.join(output_dir, "architecture_analysis.json"), "w") as f:
            json.dump(arch_result, f, indent=2)

        logger.info(f"Architecture analysis complete: {arch_result['status']}")

    # Perform a detailed analysis on sample files
    # (limiting to a few files to avoid overwhelming the system)
    sample_files = python_files[:5]  # Adjust number as needed

    for file_path in sample_files:
        rel_path = os.path.relpath(file_path, project_root)
        logger.info(f"Analyzing file: {rel_path}")

        try:
            with open(file_path, "r") as f:
                file_content = f.read()

            # Create a plan for this specific file
            file_plan = registry.dispatch(
                "planner",
                {
                    "command": "create_plan",
                    "description": f"Perform comprehensive analysis of file {rel_path}",
                    "context": {
                        "file_path": file_path,
                        "file_content": file_content,
                        "language": "python",
                    },
                },
            )

            if file_plan["status"] == "success":
                plan_id = file_plan["plan_id"]

                # Execute the file analysis plan
                file_result = registry.dispatch(
                    "planner", {"command": "execute_plan", "plan_id": plan_id}
                )

                # Save file analysis results
                safe_filename = rel_path.replace("/", "_").replace("\\", "_")
                with open(
                    os.path.join(output_dir, f"{safe_filename}_analysis.json"), "w"
                ) as f:
                    json.dump(file_result, f, indent=2)

                # Store insights in vector memory
                if file_result["status"] == "success":
                    registry.dispatch(
                        "vector_memory",
                        {
                            "command": "add",
                            "content": f"Analysis of {rel_path}: {json.dumps(file_result)}",
                            "metadata": {
                                "type": "file_analysis",
                                "file_path": rel_path,
                                "plan_id": plan_id,
                            },
                        },
                    )
        except Exception as e:
            logger.error(f"Error analyzing {rel_path}: {str(e)}")

    # Perform a dependency analysis
    dependency_analysis = registry.dispatch(
        "dependency_management",
        {"command": "analyze_project", "project_root": project_root},
    )

    # Save dependency analysis
    with open(os.path.join(output_dir, "dependency_analysis.json"), "w") as f:
        json.dump(dependency_analysis, f, indent=2)

    # Search for relevant patterns and best practices
    patterns_search = registry.dispatch(
        "vector_memory",
        {
            "command": "search",
            "content": "python code organization patterns and best practices for agent-based systems",
            "limit": 10,
        },
    )

    # Generate final report with improvement recommendations
    final_plan = registry.dispatch(
        "planner",
        {
            "command": "create_plan",
            "description": "Generate a comprehensive report on the MindMeld codebase with recommendations for improvements",
            "context": {
                "project_root": project_root,
                "architecture_analysis": "architecture_analysis.json",
                "file_analyses": [
                    f"{safe_filename}_analysis.json"
                    for safe_filename in [
                        os.path.relpath(f, project_root)
                        .replace("/", "_")
                        .replace("\\", "_")
                        for f in sample_files
                    ]
                ],
                "dependency_analysis": "dependency_analysis.json",
                "patterns_search": patterns_search,
            },
        },
    )

    if final_plan["status"] == "success":
        plan_id = final_plan["plan_id"]

        # Execute final report generation
        final_result = registry.dispatch(
            "planner", {"command": "execute_plan", "plan_id": plan_id}
        )

        # Save final report
        with open(os.path.join(output_dir, "final_report.json"), "w") as f:
            json.dump(final_result, f, indent=2)

        logger.info(f"Final report generated: {final_result['status']}")

        # Print summary of findings
        print("\n" + "=" * 80)
        print("MINDMELD CODEBASE ANALYSIS SUMMARY")
        print("=" * 80)

        for _, result in final_result.get("task_results", {}).items():
            if result.get("status") == "success" and "summary" in result:
                print(f"\n{result['summary']}")

        print("\nFull analysis results available in:", output_dir)
        print("=" * 80 + "\n")

    return output_dir


if __name__ == "__main__":
    start_time = time.time()
    output_dir = analyze_codebase()
    elapsed_time = time.time() - start_time
    logger.info(f"Analysis completed in {elapsed_time:.2f} seconds")

    if output_dir:
        print(f"\nAnalysis results are available in: {output_dir}")
        print("You can review the following files:")
        print("- architecture_analysis.json: Overall architecture assessment")
        print("- dependency_analysis.json: Project dependencies assessment")
        print("- [filename]_analysis.json: Individual file analyses")
        print("- final_report.json: Comprehensive report with recommendations")
