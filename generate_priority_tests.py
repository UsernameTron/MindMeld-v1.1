#!/usr/bin/env python3
"""
Example script to demonstrate using the enhanced test generator
with priority modules and specific templates.

This script shows how to generate tests for high-priority modules
with appropriate templates and debugging support.
"""

import argparse
import os
import subprocess


def main():
    parser = argparse.ArgumentParser(
        description="Generate tests for high-priority modules"
    )
    parser.add_argument(
        "--modules",
        "-m",
        nargs="+",
        default=["file_operations", "api_client", "auth"],
        help="List of high-priority module names",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="tests/enhanced_generated",
        help="Output directory for generated tests",
    )
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Run CodeDebugAgent on generated tests",
    )
    args = parser.parse_args()

    # Map modules to appropriate templates
    template_mapping = {
        "file_operations": "file",
        "fs": "file",
        "storage": "file",
        "io": "file",
        "auth": "auth",
        "user": "auth",
        "permission": "auth",
        "security": "auth",
        "api": "api",
        "model": "api",
        "llm": "api",
        "client": "api",
    }

    print(f"Generating tests for high-priority modules: {args.modules}")

    # Create output directory
    os.makedirs(args.output, exist_ok=True)

    # Process each module with the appropriate template
    for module in args.modules:
        # Determine template based on module name
        template = "general"
        for key, value in template_mapping.items():
            if key in module:
                template = value
                break

        # Find matching files in src directory
        for root, _, files in os.walk("src"):
            for file in files:
                if module in file and file.endswith(".py"):
                    file_path = os.path.join(root, file)

                    # Build the command
                    cmd = [
                        "python",
                        "run_test_generator.py",
                        "--single",
                        "--enhance",
                        f"--template={template}",
                        f"--path={file_path}",
                        f"--output={args.output}",
                    ]

                    # Add debug flag if requested
                    if args.debug:
                        cmd.append("--debug")

                    print(f"Processing {file_path} with {template} template...")
                    try:
                        subprocess.run(cmd, check=True)
                        print(f"Successfully generated tests for {file_path}")
                    except subprocess.CalledProcessError as e:
                        print(f"Error generating tests for {file_path}: {e}")


if __name__ == "__main__":
    main()
