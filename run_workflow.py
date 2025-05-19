#!/usr/bin/env python3

import argparse
import json
import os
import sys

from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree

from src.agents.implementations.code_debug import CodeDebugAgent
from src.agents.implementations.dependency_management import DependencyManagementAgent
from src.agents.implementations.orchestrator import OrchestratorAgent
from src.agents.implementations.test_generator import TestGeneratorAgent
from src.agents.workflows.code_quality import WORKFLOWS

console = Console()


def main():
    parser = argparse.ArgumentParser(description="Run agent workflows on your code")
    parser.add_argument(
        "--workflow",
        "-w",
        required=True,
        choices=WORKFLOWS.keys(),
        help="Workflow to execute",
    )
    parser.add_argument(
        "--path", "-p", required=True, help="Path to the file or directory to process"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="workflow_results",
        help="Output directory for workflow results",
    )
    parser.add_argument(
        "--continue-on-error",
        "-c",
        action="store_true",
        help="Continue workflow execution even if a step fails",
    )
    args = parser.parse_args()

    # Check if path exists
    if not os.path.exists(args.path):
        console.print(f"[red]Error: Path not found: {args.path}[/red]")
        sys.exit(1)

    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)

    # Initialize the orchestrator agent
    orchestrator = OrchestratorAgent()

    # Create and register agent instances
    code_debug_agent = CodeDebugAgent()
    dependency_agent = DependencyManagementAgent()
    test_generator_agent = TestGeneratorAgent()

    # Register agent instances with the orchestrator
    orchestrator.register_agent_instance("code_debug", code_debug_agent)
    orchestrator.register_agent_instance("dependency_management", dependency_agent)
    orchestrator.register_agent_instance("test_generator", test_generator_agent)

    # Register workflows
    for name, workflow in WORKFLOWS.items():
        orchestrator.register_workflow(name, workflow)

    # Prepare workflow input
    is_file = os.path.isfile(args.path)

    if is_file:
        with open(args.path, "r") as f:
            code = f.read()

        workflow_input = {"code": code, "file_path": args.path}
    else:
        workflow_input = {"directory": args.path}

    # Prepare workflow options
    workflow_options = {
        "continue_on_error": args.continue_on_error,
        "output_directory": args.output,
    }

    # Execute the workflow
    console.print(
        Panel(f"[bold]Running {args.workflow} workflow on {args.path}[/bold]")
    )

    result = orchestrator.process(
        {
            "workflow": args.workflow,
            "input": workflow_input,
            "options": workflow_options,
        }
    )

    # Handle workflow errors
    if "error" in result:
        console.print(f"[red]Workflow error: {result['error']}[/red]")
        sys.exit(1)

    # Display workflow results
    display_workflow_results(result, args.workflow)

    # Save results to file
    output_file = os.path.join(args.output, f"{args.workflow}_results.json")
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)

    console.print(f"\nResults saved to: [green]{output_file}[/green]")


def display_workflow_results(results, workflow_name):
    """Display the workflow results in a tree structure."""
    tree = Tree(f"[bold]{workflow_name} Workflow Results[/bold]")

    # Add completed steps
    completed = tree.add("[green]Completed Steps[/green]")
    for step in results.get("completed_steps", []):
        completed.add(f"[green]{step}[/green]")

    # Add errors if any
    if results.get("errors"):
        errors = tree.add("[red]Errors[/red]")
        for error in results["errors"]:
            step_id = error.get("step_id", "unknown")
            error_msg = error.get("error", "Unknown error")
            errors.add(f"[red]{step_id}: {error_msg}[/red]")

    # Add results summary
    summary = tree.add("[cyan]Results Summary[/cyan]")

    # Code debug results
    if "results" in results and "debug" in results["results"]:
        debug_results = results["results"]["debug"]
        issues_count = len(debug_results.get("issues", []))
        summary.add(f"[cyan]Code Issues: {issues_count}[/cyan]")

    # Dependency results
    if "results" in results and "dependency" in results["results"]:
        dep_results = results["results"]["dependency"]
        missing_count = len(dep_results.get("missing_dependencies", []))
        vuln_count = len(dep_results.get("vulnerabilities", []))
        summary.add(f"[cyan]Missing Dependencies: {missing_count}[/cyan]")
        summary.add(f"[cyan]Security Vulnerabilities: {vuln_count}[/cyan]")

    # Test generation results
    if "results" in results and "test_gen" in results["results"]:
        test_results = results["results"]["test_gen"]
        coverage = test_results.get("coverage_estimate", 0)
        summary.add(f"[cyan]Test Coverage: {coverage:.1f}%[/cyan]")

    console.print(tree)


if __name__ == "__main__":
    main()
