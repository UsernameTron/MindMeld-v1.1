#!/usr/bin/env python3
"""
Examples of using the MindMeld utilities for common tasks.

This script demonstrates how to use the utilities for file operations,
error handling, and LLM interactions.
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.error_handling import (
    FileProcessingError,
    LLMCallError,
    MindMeldError,
    ValidationError,
)
from utils.file_operations import (
    path_exists,
    process_files_parallel,
    read_file,
    should_process_file,
    write_json,
)
from utils.llm_client import call_llm_with_retry, get_default_model, with_fallback_model


def file_operations_example(directory: str) -> None:
    """
    Demonstrate file operations utilities.

    Args:
        directory: Directory to process
    """
    print("\n=== File Operations Examples ===\n")

    try:
        # Create a directory if it doesn't exist
        output_dir = Path("examples/output")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Read a file safely
        try:
            readme_path = Path(directory) / "README.md"
            if path_exists(readme_path):
                content = read_file(readme_path)
                print(f"Read README.md: {len(content)} characters")
            else:
                print(f"README.md not found in {directory}")
        except FileProcessingError as e:
            print(f"Error reading README.md: {e}")

        # Filter Python files in a directory
        python_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = Path(root) / file
                if should_process_file(file_path, extensions=[".py"]):
                    python_files.append(file_path)

        print(f"Found {len(python_files)} Python files")

        # Process multiple files in parallel
        def count_lines(file_path: Path) -> Dict[str, Any]:
            """Count the number of lines in a file."""
            try:
                content = read_file(file_path)
                line_count = len(content.splitlines())
                return {"file": str(file_path), "lines": line_count}
            except FileProcessingError:
                return {"file": str(file_path), "error": "Failed to read file"}

        # Process up to 10 files
        files_to_process = python_files[:10]
        print(f"Processing {len(files_to_process)} files in parallel...")

        start_time = time.time()
        results = process_files_parallel(files_to_process, count_lines)
        end_time = time.time()

        print(f"Processed {len(results)} files in {end_time - start_time:.2f} seconds")

        # Write the results to a JSON file
        results_file = output_dir / "file_stats.json"
        write_json(results_file, {"files": results})
        print(f"Wrote results to {results_file}")

    except MindMeldError as e:
        print(f"Error in file operations example: {e}")


def error_handling_example() -> None:
    """Demonstrate error handling utilities."""
    print("\n=== Error Handling Examples ===\n")

    # Create a function that might raise different errors
    def process_with_error(error_type: str) -> None:
        """Raise different types of errors for demonstration."""
        if error_type == "file":
            raise FileProcessingError("Could not process file")
        elif error_type == "validation":
            raise ValidationError("Invalid input data")
        elif error_type == "llm":
            raise LLMCallError("Failed to call LLM", model_name="phi3.5:latest")
        elif error_type == "none":
            print("No error occurred")
        else:
            raise MindMeldError(f"Unknown error type: {error_type}")

    # Handle each error type
    for error_type in ["file", "validation", "llm", "none", "unknown"]:
        try:
            print(f"Trying with error_type='{error_type}'...")
            process_with_error(error_type)
            print("  Success!")
        except MindMeldError as e:
            # All our custom errors inherit from MindMeldError
            print(f"  Caught error: {e.__class__.__name__}: {e}")

    # Create standardized error report
    def create_error_report(e: MindMeldError) -> Dict[str, Any]:
        """Create a standardized error report from an exception."""
        report = {
            "status": "error",
            "error": {"message": str(e), "type": e.__class__.__name__},
            "timestamp": int(time.time()),
        }

        # Add model info for LLM errors
        if isinstance(e, LLMCallError) and e.model_name:
            report["model"] = e.model_name

        return report

    # Example of using the error report function
    try:
        raise LLMCallError("Failed to call LLM", model_name="phi3.5:latest")
    except MindMeldError as e:
        error_report = create_error_report(e)
        print(f"Error report: {json.dumps(error_report, indent=2)}")


def llm_client_example() -> None:
    """Demonstrate LLM client utilities."""
    print("\n=== LLM Client Examples ===\n")

    # Show information about the default model
    model = get_default_model()
    print(f"Default model: {model}")

    # Example of using the retry decorator
    @call_llm_with_retry(max_retries=3)
    def generate_with_retry(prompt: str) -> str:
        """Generate text with retry logic."""
        print(f"Calling LLM with prompt: {prompt[:30]}...")
        # This is a simulation - the real function would call the LLM
        if "fail" in prompt.lower():
            raise LLMCallError("Simulated failure")
        return f"Response to: {prompt[:10]}..."

    # Example of using the fallback model decorator
    @with_fallback_model("llama2")
    def generate_with_fallback(prompt: str, model_name: Optional[str] = None) -> str:
        """Generate text with fallback to another model."""
        print(f"Using model: {model_name or get_default_model()}")
        # This is a simulation - the real function would call the LLM
        if model_name == "unavailable_model":
            raise LLMCallError("Model unavailable")
        return f"Response from {model_name or get_default_model()}: {prompt[:10]}..."

    # Try the retry function
    prompts = ["Tell me about MindMeld", "This should fail", "Another prompt"]
    for prompt in prompts:
        try:
            response = generate_with_retry(prompt)
            print(f"  Response: {response}")
        except LLMCallError as e:
            print(f"  Error: {e}")

    # Try the fallback function
    print("\nTesting fallback functionality:")
    for model_name in ["phi3.5:latest", "unavailable_model", None]:
        try:
            response = generate_with_fallback(
                "Tell me about fallbacks", model_name=model_name
            )
            print(f"  {response}")
        except LLMCallError as e:
            print(f"  Error: {e}")


def main() -> None:
    """Run all examples."""
    if len(sys.argv) < 2:
        print("Usage: python examples.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]

    file_operations_example(directory)
    error_handling_example()
    llm_client_example()

    print("\nAll examples completed.")


if __name__ == "__main__":
    main()
