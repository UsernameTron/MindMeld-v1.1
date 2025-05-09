#!/usr/bin/env python
"""
Docstring Audit Tool for MindMeld.

This script scans Python files in the MindMeld codebase to identify functions,
methods, and classes that are missing docstrings or don't follow Google-style
documentation standards.
"""

import ast
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


@dataclass
class DocstringIssue:
    """Represents an issue with a docstring."""

    file_path: str
    line_number: int
    name: str
    type: str  # 'function', 'method', 'class'
    issue: str  # 'missing', 'wrong_format', etc.


def is_google_style_docstring(docstring: str) -> bool:
    """
    Check if a docstring follows Google-style format.

    Args:
        docstring (str): The docstring to check.

    Returns:
        bool: True if the docstring follows Google style, False otherwise.
    """
    if not docstring:
        return False

    # Clean up the docstring
    docstring = docstring.strip()

    # Very basic Google-style docstring check - look for sections
    google_sections = ["Args:", "Returns:", "Raises:", "Examples:"]

    # Check if at least one section exists
    return any(section in docstring for section in google_sections)


def scan_file(file_path: str) -> List[DocstringIssue]:
    """
    Scan a Python file for docstring issues.

    Args:
        file_path (str): Path to the Python file.

    Returns:
        List[DocstringIssue]: List of docstring issues found.
    """
    issues = []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        tree = ast.parse(content, filename=file_path)

        # Scan for module-level docstring
        if not ast.get_docstring(tree):
            issues.append(
                DocstringIssue(
                    file_path=file_path,
                    line_number=1,
                    name=os.path.basename(file_path),
                    type="module",
                    issue="missing",
                )
            )

        # Scan classes and functions
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                docstring = ast.get_docstring(node)

                if not docstring:
                    issues.append(
                        DocstringIssue(
                            file_path=file_path,
                            line_number=node.lineno,
                            name=node.name,
                            type=(
                                "class"
                                if isinstance(node, ast.ClassDef)
                                else "function"
                            ),
                            issue="missing",
                        )
                    )
                elif not is_google_style_docstring(docstring):
                    issues.append(
                        DocstringIssue(
                            file_path=file_path,
                            line_number=node.lineno,
                            name=node.name,
                            type=(
                                "class"
                                if isinstance(node, ast.ClassDef)
                                else "function"
                            ),
                            issue="wrong_format",
                        )
                    )
    except Exception as e:
        print(f"Error scanning file {file_path}: {str(e)}")

    return issues


def scan_directory(
    directory: str, exclude_dirs: Set[str] = None
) -> List[DocstringIssue]:
    """
    Recursively scan a directory for Python files with docstring issues.

    Args:
        directory (str): Directory to scan.
        exclude_dirs (Set[str], optional): Directories to exclude from scanning.

    Returns:
        List[DocstringIssue]: List of docstring issues found.
    """
    if exclude_dirs is None:
        exclude_dirs = {
            ".venv",
            ".git",
            "__pycache__",
            "build",
            "dist",
            ".pytest_cache",
        }

    issues = []

    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                issues.extend(scan_file(file_path))

    return issues


def generate_report(issues: List[DocstringIssue]) -> Dict[str, Any]:
    """
    Generate a report from the list of issues.

    Args:
        issues (List[DocstringIssue]): List of docstring issues.

    Returns:
        Dict[str, Any]: Report data.
    """
    missing_count = sum(1 for issue in issues if issue.issue == "missing")
    wrong_format_count = sum(1 for issue in issues if issue.issue == "wrong_format")

    # Group issues by file
    files_with_issues = {}
    for issue in issues:
        if issue.file_path not in files_with_issues:
            files_with_issues[issue.file_path] = []
        files_with_issues[issue.file_path].append(issue)

    # Group issues by type
    issues_by_type = {
        "module": [i for i in issues if i.type == "module"],
        "class": [i for i in issues if i.type == "class"],
        "function": [i for i in issues if i.type == "function"],
    }

    return {
        "total_issues": len(issues),
        "missing_count": missing_count,
        "wrong_format_count": wrong_format_count,
        "files_with_issues": files_with_issues,
        "issues_by_type": issues_by_type,
    }


def print_report(report: Dict[str, Any], verbose: bool = False) -> None:
    """
    Print a human-readable report.

    Args:
        report (Dict[str, Any]): Report data.
        verbose (bool, optional): Whether to print detailed information.
    """
    print("\n==== MindMeld Docstring Audit Report ====")
    print(f"Total issues: {report['total_issues']}")
    print(f"Missing docstrings: {report['missing_count']}")
    print(f"Non-Google style docstrings: {report['wrong_format_count']}")
    print(f"Files with issues: {len(report['files_with_issues'])}")

    print("\n--- Issues by Type ---")
    for type_name, type_issues in report["issues_by_type"].items():
        print(f"{type_name.capitalize()}: {len(type_issues)}")

    if verbose:
        print("\n=== Detailed Issues ===")
        for file_path, file_issues in report["files_with_issues"].items():
            print(f"\nFile: {file_path}")
            for issue in file_issues:
                print(
                    f"  Line {issue.line_number}: {issue.type} '{issue.name}' - {issue.issue}"
                )

    # Priority recommendations
    print("\n=== Recommended Priority Files ===")
    # Sort files by number of issues
    sorted_files = sorted(
        report["files_with_issues"].items(), key=lambda x: len(x[1]), reverse=True
    )

    # Show top 5 files with most issues
    for i, (file_path, file_issues) in enumerate(sorted_files[:5], 1):
        if "/services/" in file_path or "/api/" in file_path:
            priority = "HIGH"
        else:
            priority = "MEDIUM"
        print(f"{i}. {file_path} - {len(file_issues)} issues (Priority: {priority})")


def main() -> None:
    """Run the docstring audit."""
    import argparse

    parser = argparse.ArgumentParser(description="Audit docstrings in Python files")
    parser.add_argument("--directory", "-d", default=".", help="Directory to scan")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Print detailed information"
    )
    args = parser.parse_args()

    print(f"Scanning directory: {args.directory}")
    issues = scan_directory(args.directory)
    report = generate_report(issues)
    print_report(report, verbose=args.verbose)


if __name__ == "__main__":
    main()
