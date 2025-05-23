#!/usr/bin/env python3
"""
Script to update tool definitions in agent files to use the new Claude 3.7 API format.
"""

import argparse
import os
import re


def update_tools_in_file(file_path, dry_run=False):
    """Update tool definitions in the given file to use the new format."""
    with open(file_path, "r") as f:
        content = f.read()

    # Define regex patterns for common tool definitions
    patterns = [
        # Match function tool type definitions and replace with appropriate type
        (r'"type"\s*:\s*"function"', '"type": "custom"'),  # Default to custom
        (r"'type'\s*:\s*'function'", "'type': 'custom'"),  # Single quotes version
        # Handle specific functions that map to specific tools
        # Double quotes versions
        (
            r'"name"\s*:\s*"execute_bash".*?"type"\s*:\s*"function"',
            '"name": "execute_bash"\\g<0>'.replace('"function"', '"bash_20250124"'),
        ),
        (
            r'"name"\s*:\s*"search_web".*?"type"\s*:\s*"function"',
            '"name": "search_web"\\g<0>'.replace('"function"', '"web_search_20250305"'),
        ),
        (
            r'"name"\s*:\s*"edit_text".*?"type"\s*:\s*"function"',
            '"name": "edit_text"\\g<0>'.replace('"function"', '"text_editor_20250429"'),
        ),
        (
            r'"name"\s*:\s*"browse_web".*?"type"\s*:\s*"function"',
            '"name": "browse_web"\\g<0>'.replace(
                '"function"', '"web_browser_20250428"'
            ),
        ),
        (
            r'"name"\s*:\s*"retrieve_content".*?"type"\s*:\s*"function"',
            '"name": "retrieve_content"\\g<0>'.replace(
                '"function"', '"retrieval_20250301"'
            ),
        ),
        # Single quotes versions
        (
            r"'name'\s*:\s*'execute_bash'.*?'type'\s*:\s*'function'",
            "'name': 'execute_bash'\\g<0>".replace("'function'", "'bash_20250124'"),
        ),
        (
            r"'name'\s*:\s*'search_web'.*?'type'\s*:\s*'function'",
            "'name': 'search_web'\\g<0>".replace("'function'", "'web_search_20250305'"),
        ),
        (
            r"'name'\s*:\s*'edit_text'.*?'type'\s*:\s*'function'",
            "'name': 'edit_text'\\g<0>".replace("'function'", "'text_editor_20250429'"),
        ),
        (
            r"'name'\s*:\s*'browse_web'.*?'type'\s*:\s*'function'",
            "'name': 'browse_web'\\g<0>".replace(
                "'function'", "'web_browser_20250428'"
            ),
        ),
        (
            r"'name'\s*:\s*'retrieve_content'.*?'type'\s*:\s*'function'",
            "'name': 'retrieve_content'\\g<0>".replace(
                "'function'", "'retrieval_20250301'"
            ),
        ),
    ]

    updated_content = content
    changes_made = False

    for pattern, replacement in patterns:
        new_content = re.sub(pattern, replacement, updated_content)
        if new_content != updated_content:
            changes_made = True
            updated_content = new_content

    if changes_made:
        print(f"Changes needed in {file_path}")
        if not dry_run:
            print(f"Updating {file_path}")
            # Create backup
            backup_path = f"{file_path}.bak"
            with open(backup_path, "w") as f:
                f.write(content)
            # Write updated content
            with open(file_path, "w") as f:
                f.write(updated_content)
            print(f"Created backup at {backup_path}")
        else:
            print("Dry run - no changes made")
    else:
        print(f"No changes needed in {file_path}")

    return changes_made


def main():
    parser = argparse.ArgumentParser(
        description="Update tool definitions in agent files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )
    args = parser.parse_args()

    # Define the base path for agent directories
    base_path = "packages/agents"
    files_updated = 0

    # Get all agent types
    if os.path.exists(base_path):
        agent_types = [
            os.path.join(base_path, d)
            for d in os.listdir(base_path)
            if os.path.isdir(os.path.join(base_path, d))
        ]

        # Check for agents subdirectory in each agent type
        agent_dirs = []
        for agent_type in agent_types:
            agents_dir = os.path.join(agent_type, "agents")
            if os.path.exists(agents_dir) and os.path.isdir(agents_dir):
                agent_dirs.append(agents_dir)

        print(f"Found agent directories: {agent_dirs}")
    else:
        agent_dirs = []
        print(f"Base path {base_path} not found")

    for agent_dir in agent_dirs:
        if os.path.exists(agent_dir):
            for file in os.listdir(agent_dir):
                if file.endswith(".py"):
                    file_path = os.path.join(agent_dir, file)
                    if update_tools_in_file(file_path, args.dry_run):
                        files_updated += 1

    print(
        f"\nSummary: {'Would update' if args.dry_run else 'Updated'} {files_updated} files"
    )


if __name__ == "__main__":
    main()
