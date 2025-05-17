#!/usr/bin/env python3
"""
Test script to verify the input validation and schema compliance of the agent pipeline.
"""

import argparse
import os
import sys
import json
import tempfile
from pathlib import Path

# Add the current directory to the Python path to import project modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_test_file(content: str, suffix: str = ".py") -> str:
    """Create a temporary test file with the given content."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content.encode('utf-8'))
        return tmp.name

def create_test_directory() -> str:
    """Create a temporary test directory."""
    temp_dir = tempfile.mkdtemp()
    return temp_dir

def run_tests():
    """Run a series of tests to validate our fixes."""
    import subprocess
    from schema_validator import validate_agent_output, load_schema
    
    print("\n🔍 Running validation tests for agent pipeline...\n")
    
    # Test 1: Valid file input for CodeRepairAgent
    print("Test 1: Valid file input for CodeRepairAgent")
    valid_file = create_test_file("def add(a, b):\n    return a + b\n")
    try:
        result = subprocess.run(
            ["python", "run_agent.py", "CodeRepairAgent", valid_file],
            capture_output=True,
            text=True,
            check=False
        )
        print(f"Exit code: {result.returncode}")
        print(f"Output: {result.stdout}")
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
        
        # Verify output file exists and contains valid schema
        if Path("reports/CodeRepairAgent").exists():
            latest_report = max(
                Path("reports/CodeRepairAgent").glob("*.json"),
                key=lambda p: p.stat().st_mtime,
                default=None
            )
            if latest_report:
                with open(latest_report) as f:
                    report_data = json.load(f)
                valid, error = validate_agent_output(report_data)
                print(f"Report schema valid: {valid}")
                if not valid:
                    print(f"Validation error: {error}")
    finally:
        os.unlink(valid_file)
    
    # Test 2: Directory input for CodeRepairAgent (should fail with validation error)
    print("\nTest 2: Directory input for CodeRepairAgent (should fail with validation)")
    test_dir = create_test_directory()
    try:
        result = subprocess.run(
            ["python", "run_agent.py", "CodeRepairAgent", test_dir],
            capture_output=True,
            text=True,
            check=False
        )
        print(f"Exit code: {result.returncode}")
        print(f"Output: {result.stdout}")
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
        
        # Verify output file exists and contains expected error
        if Path("reports/CodeRepairAgent").exists():
            latest_report = max(
                Path("reports/CodeRepairAgent").glob("*.json"),
                key=lambda p: p.stat().st_mtime,
                default=None
            )
            if latest_report:
                with open(latest_report) as f:
                    report_data = json.load(f)
                if report_data.get("status") == "error" and "directory" in report_data.get("error", {}).get("message", ""):
                    print("✅ Correctly rejected directory input with appropriate error")
                else:
                    print("❌ Failed to properly reject directory input")
    finally:
        os.rmdir(test_dir)
    
    # Test 3: Non-integer input for summarizer agent (should fail validation)
    print("\nTest 3: Non-integer input for summarizer agent")
    try:
        result = subprocess.run(
            ["python", "run_agent.py", "summarizer", "not_an_integer"],
            capture_output=True,
            text=True,
            check=False
        )
        print(f"Exit code: {result.returncode}")
        print(f"Output: {result.stdout}")
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
        
        # Verify output file exists and contains expected error
        if Path("reports/summarizer").exists():
            latest_report = max(
                Path("reports/summarizer").glob("*.json"),
                key=lambda p: p.stat().st_mtime,
                default=None
            )
            if latest_report:
                with open(latest_report) as f:
                    report_data = json.load(f)
                if report_data.get("status") == "error" and "integer" in report_data.get("error", {}).get("message", ""):
                    print("✅ Correctly rejected non-integer input with appropriate error")
                else:
                    print("❌ Failed to properly reject non-integer input")
    except Exception as e:
        print(f"Error running test: {e}")
    
    # Test 4: Valid directory input for DependencyAgent
    print("\nTest 4: Valid directory input for DependencyAgent")
    try:
        result = subprocess.run(
            ["python", "run_agent.py", "DependencyAgent", "."],
            capture_output=True,
            text=True,
            check=False
        )
        print(f"Exit code: {result.returncode}")
        print(f"Output: {result.stdout}")
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
        
        # Verify output file exists and contains valid schema
        if Path("reports/DependencyAgent").exists():
            latest_report = max(
                Path("reports/DependencyAgent").glob("*.json"),
                key=lambda p: p.stat().st_mtime,
                default=None
            )
            if latest_report:
                with open(latest_report) as f:
                    report_data = json.load(f)
                valid, error = validate_agent_output(report_data)
                print(f"Report schema valid: {valid}")
                if not valid:
                    print(f"Validation error: {error}")
    except Exception as e:
        print(f"Error running test: {e}")
    
    print("\n✅ Validation tests completed\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test the agent pipeline fixes")
    args = parser.parse_args()
    
    run_tests()
