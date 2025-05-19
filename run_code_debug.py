#!/usr/bin/env python3

import argparse
import os
import re
import shutil
import sys

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from src.agents.implementations.code_debug import CodeDebugAgent

# Initialize console for nice output
console = Console()


def analyze_file(file_path, agent, min_severity="low"):
    """Analyze a single file using the CodeDebugAgent"""
    try:
        with open(file_path, "r") as f:
            code = f.read()

        result = agent.process({"code": code})

        # Filter issues by severity if needed
        if min_severity != "low":
            severity_levels = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            min_severity_level = severity_levels.get(min_severity, 3)
            result["issues"] = [
                issue
                for issue in result["issues"]
                if severity_levels.get(issue.get("severity", "medium"), 2)
                <= min_severity_level
            ]

        return result
    except Exception as e:
        console.print(f"[red]Error analyzing {file_path}: {str(e)}[/red]")
        return {"has_errors": False, "issues": []}


def format_results(file_path, results):
    """Format the analysis results for display"""
    if not results["issues"]:
        return None

    table = Table(title=f"Issues in {file_path}")
    table.add_column("Type", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Line", style="yellow", justify="right")
    table.add_column("Severity", style="red")
    table.add_column("Fix Suggestion", style="magenta")

    for issue in results["issues"]:
        severity = issue.get("severity", "medium")
        severity_style = {
            "critical": "bold red",
            "high": "red",
            "medium": "yellow",
            "low": "green",
        }.get(severity, "yellow")

        table.add_row(
            issue.get("type", "Unknown"),
            issue.get("description", "No description"),
            str(issue.get("line", "?")),
            f"[{severity_style}]{severity.upper()}[/{severity_style}]",
            issue.get("fix", "No suggestion"),
        )

    return table


def apply_fix(file_path, issue, backup=True):
    """Apply a suggested fix to a file.

    Args:
        file_path: Path to the file to fix
        issue: The issue dict containing fix information
        backup: Whether to create a backup before applying the fix

    Returns:
        True if fix was applied successfully, False otherwise
    """
    try:
        # Create backup if requested
        if backup:
            backup_path = f"{file_path}.bak"
            shutil.copy2(file_path, backup_path)
            console.print(f"[dim]Created backup at {backup_path}[/dim]")

        with open(file_path, "r") as f:
            lines = f.readlines()

        line_idx = issue["line"] - 1
        if 0 <= line_idx < len(lines):
            # Apply the appropriate fix based on issue type and description
            if (
                issue["type"] == "syntaxerror"
                and "missing colon" in issue["description"]
            ):
                # Fix missing colon
                line = lines[line_idx]
                if not line.rstrip().endswith(":"):
                    fixed_line = line.rstrip() + ":\n"
                    lines[line_idx] = fixed_line
                    console.print(
                        f"[green]Fixed missing colon in {file_path} line {issue['line']}[/green]"
                    )

            elif (
                issue["type"] == "logicalerror"
                and "division by zero" in issue["description"]
            ):
                # Add division by zero check
                line = lines[line_idx]
                # Try to identify the variable being used as denominator
                division_match = re.search(r"/\s*(\w+|\w+\([^)]*\))", line)
                if division_match:
                    denominator = division_match.group(1)
                    indent = re.match(r"^\s*", line).group(0)
                    # Create guard condition based on the denominator
                    if "len(" in denominator:
                        # Special case for len()
                        collection = re.search(r"len\(([^)]+)\)", denominator)
                        if collection:
                            check_line = f"{indent}if not {collection.group(1)}:  # Prevent division by zero\n"
                            check_line += f"{indent}    return 0\n"
                            lines.insert(line_idx, check_line)
                            console.print(
                                f"[green]Added division by zero check for {collection.group(1)} in {file_path} line {issue['line']}[/green]"
                            )
                    else:
                        check_line = f"{indent}if {denominator} == 0:  # Prevent division by zero\n"
                        check_line += f"{indent}    return 0\n"
                        lines.insert(line_idx, check_line)
                        console.print(
                            f"[green]Added division by zero check for {denominator} in {file_path} line {issue['line']}[/green]"
                        )

            elif (
                issue["type"] == "security"
                and "command injection" in issue["description"]
            ):
                # Fix command injection vulnerability
                line = lines[line_idx]
                if "shell=True" in line and "subprocess" in line:
                    # Replace shell=True with shell=False
                    fixed_line = line.replace("shell=True", "shell=False")
                    lines[line_idx] = fixed_line
                    console.print(
                        f"[green]Fixed command injection vulnerability in {file_path} line {issue['line']}[/green]"
                    )

            elif (
                issue["type"] == "security"
                and "hardcoded credentials" in issue["description"]
            ):
                # Replace hardcoded credentials with environment variables
                line = lines[line_idx]
                # Find credential assignment
                cred_match = re.search(r'(\w+)\s*=\s*["\']([^"\']+)["\']', line)
                if cred_match:
                    var_name = cred_match.group(1)
                    indent = re.match(r"^\s*", line).group(0)
                    env_var = var_name.upper()
                    fixed_line = f"{indent}{var_name} = os.environ.get('{env_var}')  # Get from environment variable\n"
                    lines[line_idx] = fixed_line
                    console.print(
                        f"[green]Replaced hardcoded credential with environment variable in {file_path} line {issue['line']}[/green]"
                    )

            elif issue["type"] == "performance" and "o(n²)" in issue["description"]:
                # Add comment for performance improvement
                line = lines[line_idx]
                indent = re.match(r"^\s*", line).group(0)
                comment_line = f"{indent}# TODO: Consider optimizing this nested loop with a more efficient data structure\n"
                lines.insert(line_idx, comment_line)
                console.print(
                    f"[yellow]Added performance optimization comment in {file_path} line {issue['line']}[/yellow]"
                )

            else:
                console.print(
                    f"[yellow]No automatic fix available for {issue['type']} in {file_path} line {issue['line']}[/yellow]"
                )
                return False

            # Write the fixed file
            with open(file_path, "w") as f:
                f.writelines(lines)

            return True
        else:
            console.print(
                f"[red]Line {issue['line']} out of range for {file_path}[/red]"
            )
            return False

    except Exception as e:
        console.print(f"[red]Error applying fix to {file_path}: {str(e)}[/red]")
        return False


def fix_issues(issues_by_file, interactive=True):
    """Apply fixes to issues found in files.

    Args:
        issues_by_file: Dictionary mapping file paths to lists of issues
        interactive: Whether to ask for confirmation before applying each fix

    Returns:
        Number of fixes applied
    """
    fix_count = 0

    for file_path, issues in issues_by_file.items():
        # Sort issues by severity and line number
        issues.sort(
            key=lambda x: (
                {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(
                    x.get("severity", "medium"), 2
                ),
                x.get("line", 0),
            )
        )

        console.print(f"\n[bold]Fixing issues in {file_path}[/bold]")

        for issue in issues:
            severity = issue.get("severity", "medium")
            severity_color = {
                "critical": "bright_red",
                "high": "red",
                "medium": "yellow",
                "low": "green",
            }.get(severity, "yellow")

            console.print(
                f"[{severity_color}]({severity.upper()})[/{severity_color}] Line {issue['line']}: {issue['description']}"
            )
            console.print(f"Fix: {issue['fix']}")

            should_fix = True
            if interactive:
                choice = console.input("[bold]Apply this fix? (y/n/a/q): [/bold]")
                if choice.lower() == "q":
                    return fix_count
                elif choice.lower() == "a":
                    interactive = False
                elif choice.lower() != "y":
                    should_fix = False

            if should_fix and apply_fix(file_path, issue):
                fix_count += 1

    return fix_count


def main():
    parser = argparse.ArgumentParser(description="Run CodeDebugAgent on project files")
    parser.add_argument(
        "--path", "-p", default="src", help="Path to scan (default: src)"
    )
    parser.add_argument(
        "--extension", "-e", default=".py", help="File extension to scan (default: .py)"
    )
    parser.add_argument(
        "--exclude",
        "-x",
        help="Comma-separated directories to exclude",
        default="__pycache__,venv,.git",
    )
    parser.add_argument(
        "--fix", "-f", action="store_true", help="Apply suggested fixes to issues found"
    )
    parser.add_argument(
        "--auto-fix",
        "-a",
        action="store_true",
        help="Automatically apply fixes without confirmation",
    )
    parser.add_argument(
        "--min-severity",
        "-s",
        choices=["low", "medium", "high", "critical"],
        default="low",
        help="Minimum severity level to report/fix (default: low)",
    )
    args = parser.parse_args()

    # Initialize the agent
    agent = CodeDebugAgent()

    # Split exclude dirs
    exclude_dirs = [d.strip() for d in args.exclude.split(",")]

    # Track statistics
    total_files = 0
    files_with_issues = 0
    total_issues = 0
    issue_types = {}
    issues_by_severity = {"critical": [], "high": [], "medium": [], "low": []}
    issues_by_file = {}

    # Handle both single file and directory paths
    file_paths = []
    if os.path.isfile(args.path):
        # Single file mode
        file_paths = [args.path]
        console.print(Panel(f"[bold]Analyzing single file: {args.path}[/bold]"))
    else:
        # Directory mode
        console.print(
            Panel(f"[bold]Scanning {args.path} for {args.extension} files...[/bold]")
        )
        # Walk through directories to find files
        for root, dirs, files in os.walk(args.path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if file.endswith(args.extension):
                    file_paths.append(os.path.join(root, file))

    # Process all collected files
    for file_path in file_paths:
        total_files += 1

        # Show progress
        console.print(f"Analyzing: {file_path}", end="\r")

        # Analyze the file
        results = analyze_file(file_path, agent, args.min_severity)

        if results["issues"]:
            files_with_issues += 1
            total_issues += len(results["issues"])

            # Store issues by file for fixing later
            issues_by_file[file_path] = results["issues"]

            # Track issue types and severities
            for issue in results["issues"]:
                issue_type = issue.get("type", "Unknown")
                issue_types[issue_type] = issue_types.get(issue_type, 0) + 1

                severity = issue.get("severity", "medium")
                issues_by_severity[severity].append((file_path, issue))

            # Display results for this file
            formatted = format_results(file_path, results)
            if formatted:
                console.print(formatted)
                console.print("")

    # Apply fixes if requested
    if (args.fix or args.auto_fix) and issues_by_file:
        fix_count = fix_issues(issues_by_file, interactive=not args.auto_fix)
        console.print(f"\n[bold green]Applied {fix_count} fixes[/bold green]")

    # Print summary
    summary = Table(title="Scan Summary")
    summary.add_column("Metric", style="cyan")
    summary.add_column("Value", style="green")

    summary.add_row("Total files scanned", str(total_files))
    summary.add_row("Files with issues", str(files_with_issues))
    summary.add_row("Total issues found", str(total_issues))

    console.print(summary)

    # Print issue type breakdown
    if issue_types:
        types_table = Table(title="Issue Types")
        types_table.add_column("Type", style="cyan")
        types_table.add_column("Count", style="green")

        for issue_type, count in sorted(
            issue_types.items(), key=lambda x: x[1], reverse=True
        ):
            types_table.add_row(issue_type, str(count))

        console.print(types_table)

    # Print issues by severity
    if any(issues for issues in issues_by_severity.values()):
        severity_table = Table(title="Issues by Severity")
        severity_table.add_column("Severity", style="cyan")
        severity_table.add_column("Count", style="green")

        severity_order = ["critical", "high", "medium", "low"]
        for severity in severity_order:
            count = len(issues_by_severity[severity])
            if count > 0:
                severity_color = {
                    "critical": "bold red",
                    "high": "red",
                    "medium": "yellow",
                    "low": "green",
                }.get(severity, "yellow")

                severity_table.add_row(
                    f"[{severity_color}]{severity.upper()}[/{severity_color}]",
                    str(count),
                )

        console.print(severity_table)


if __name__ == "__main__":
    main()
