#!/usr/bin/env python
"""
Dependency checker script that uses the DependencyManagementAgent to analyze
Python code, requirements files, and generate installation commands.
"""

import argparse
import os
from typing import Any, Dict, List

from packages.agents.claude_agents.agents.dependency_management import (
    DependencyManagementAgent,
)


def read_file(file_path: str) -> str:
    """Read a file and return its contents as a string."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return ""


def analyze_python_file(
    agent: DependencyManagementAgent, file_path: str
) -> Dict[str, Any]:
    """Analyze a Python file for dependencies."""
    print(f"Analyzing file: {file_path}")
    code = read_file(file_path)
    if not code:
        return {}

    result = agent.process({"code": code})
    return result


def analyze_requirements_file(
    agent: DependencyManagementAgent, file_path: str
) -> Dict[str, Any]:
    """Analyze a requirements file for dependencies, conflicts, and vulnerabilities."""
    print(f"Analyzing requirements file: {file_path}")
    requirements_content = read_file(file_path)
    if not requirements_content:
        return {}

    result = agent.process({"requirements_content": requirements_content})
    return result


def find_python_files(path: str) -> List[str]:
    """Find all Python files in the given path."""
    if os.path.isfile(path) and path.endswith(".py"):
        return [path]

    python_files = []
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    return python_files


def find_requirements_files(path: str = None) -> List[str]:
    """Find all requirements files in the given path."""
    if (
        path
        and os.path.isfile(path)
        and (path.endswith("requirements.txt") or "requirements" in path)
    ):
        return [path]

    search_path = path if path else "."
    requirements_files = []

    # Look for requirements.txt files
    for root, _, files in os.walk(search_path):
        for file in files:
            if (
                file == "requirements.txt"
                or file == "requirements-dev.txt"
                or ("requirements" in file and file.endswith(".txt"))
            ):
                requirements_files.append(os.path.join(root, file))

    return requirements_files


def print_dependencies(dependencies: List[str], label: str) -> None:
    """Print a list of dependencies with a label."""
    if dependencies:
        print(f"\n{label}:")
        for dep in dependencies:
            if dep.strip():  # Only print non-empty dependencies
                print(f"  - {dep}")


def print_conflicts(conflicts: List[Dict[str, Any]]) -> None:
    """Print version conflicts information."""
    if conflicts:
        print("\nVersion Conflicts:")
        for conflict in conflicts:
            package = conflict["package"]
            specs = conflict.get("specifications", [])
            print(f"  - {package}: {' vs '.join(specs)}")


def print_vulnerabilities(vulnerabilities: List[Dict[str, Any]]) -> None:
    """Print security vulnerabilities information."""
    if vulnerabilities:
        print("\nSecurity Vulnerabilities:")
        for vuln in vulnerabilities:
            package = vuln["package"]
            version = vuln.get("version", "unknown")
            cve_ids = vuln.get("cve_ids", [])
            print(f"  - {package} {version}: {', '.join(cve_ids)}")


def print_commands(commands: List[str]) -> None:
    """Print installation commands."""
    if commands:
        print("\nInstallation Commands:")
        for cmd in commands:
            print(f"  $ {cmd}")


def format_results(result: Dict[str, Any], verbose: bool = False) -> None:
    """Print the analysis results in a readable format."""
    if not result:
        print("No results to display.")
        return

    print("\n" + "=" * 50)
    print("DEPENDENCY ANALYSIS RESULTS")
    print("=" * 50)

    print_dependencies(result.get("required_dependencies", []), "Required Dependencies")
    print_dependencies(result.get("missing_dependencies", []), "Missing Dependencies")
    print_conflicts(result.get("version_conflicts", []))
    print_vulnerabilities(result.get("vulnerabilities", []))
    print_commands(result.get("installation_commands", []))

    if verbose:
        print("\nFull Analysis Results:")
        import json

        print(json.dumps(result, indent=2))

    print("\n" + "=" * 50 + "\n")


def merge_results(
    combined_results: Dict[str, Any], new_results: Dict[str, Any]
) -> None:
    """Merge new results into the combined results."""
    for key in combined_results:
        if key in new_results:
            if isinstance(new_results[key], list):
                for item in new_results[key]:
                    if item not in combined_results[key]:
                        combined_results[key].append(item)


def analyze_python_files(
    agent: DependencyManagementAgent, path: str, combined_results: Dict[str, Any]
) -> None:
    """Analyze Python files in the given path and update combined results."""
    python_files = find_python_files(path)
    print(f"Found {len(python_files)} Python files to analyze")

    for file_path in python_files:
        result = analyze_python_file(agent, file_path)
        merge_results(combined_results, result)


def analyze_requirements_files_path(
    agent: DependencyManagementAgent, combined_results: Dict[str, Any]
) -> None:
    """Analyze requirements files and update combined results."""
    requirements_files = find_requirements_files()
    print(f"Found {len(requirements_files)} requirements files to analyze")

    for file_path in requirements_files:
        result = analyze_requirements_file(agent, file_path)
        merge_results(combined_results, result)


def analyze_error_trace_file(
    agent: DependencyManagementAgent, error_path: str, combined_results: Dict[str, Any]
) -> None:
    """Analyze error trace file and update combined results."""
    error_trace = read_file(error_path)
    if error_trace:
        print(f"Analyzing error trace from: {error_path}")
        result = agent.process({"error_traceback": error_trace})
        merge_results(combined_results, result)


def main():
    parser = argparse.ArgumentParser(description="Analyze Python dependencies.")
    parser.add_argument(
        "--path", "-p", help="Path to a Python file or directory to analyze"
    )
    parser.add_argument(
        "--requirements", "-r", action="store_true", help="Analyze requirements files"
    )
    parser.add_argument(
        "--install", "-i", action="store_true", help="Generate installation commands"
    )
    parser.add_argument("--error", "-e", help="Path to error trace file")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Print verbose output"
    )

    args = parser.parse_args()

    # Initialize agent
    agent = DependencyManagementAgent()

    combined_results = {
        "required_dependencies": [],
        "missing_dependencies": [],
        "version_conflicts": [],
        "installation_commands": [],
        "vulnerabilities": [],
    }

    # Analyze Python files
    if args.path:
        analyze_python_files(agent, args.path, combined_results)

    # Analyze requirements files
    if args.requirements:
        analyze_requirements_files_path(agent, combined_results)

    # Analyze error trace file
    if args.error:
        analyze_error_trace_file(agent, args.error, combined_results)

    # Generate installation commands if --install flag is set
    if args.install and combined_results["missing_dependencies"]:
        # Use the public method to generate installation commands
        if hasattr(agent, "generate_install_commands") and callable(
            getattr(agent, "generate_install_commands", None)
        ):
            combined_results["installation_commands"] = agent.generate_install_commands(
                combined_results
            )
        else:
            print(
                "Installation command generation is not available via the public API. Please implement a public method in DependencyManagementAgent for this functionality."
            )

    # Print combined results


if __name__ == "__main__":
    main()
