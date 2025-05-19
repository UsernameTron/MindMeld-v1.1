#!/usr/bin/env python3
"""
Quick test script to verify the enhanced test generator works correctly
on the file_operations module.
"""

import os
import subprocess
import sys


def main():
    # Ensure the output directory exists
    output_dir = "tests/test_generator_demo"
    os.makedirs(output_dir, exist_ok=True)

    # Define the target module for our test
    target_file = "src/utils/file_operations.py"

    # Check if the file exists
    if not os.path.exists(target_file):
        print(f"Error: Target file {target_file} does not exist.")
        return 1

    # Run the test generator with the file template
    cmd = [
        "python",
        "run_test_generator.py",
        "--single",
        "--enhance",
        "--template=file",
        f"--path={target_file}",
        f"--output={output_dir}",
    ]

    print("Running enhanced test generator on file_operations.py...")
    try:
        subprocess.run(cmd, check=True)

        # Check if the output file was created
        output_file = os.path.join(output_dir, "test_file_operations.py")
        if os.path.exists(output_file):
            print(f"Success! Generated test file: {output_file}")

            # Try running the generated test to verify it's valid
            test_cmd = ["python", "run_specific_tests.py", output_file]
            print("\nVerifying the generated test runs correctly...")
            try:
                subprocess.run(test_cmd, check=True)
                print("\nTest execution successful! The generated test is valid.")
                return 0
            except subprocess.CalledProcessError:
                print(
                    "\nWarning: The generated test has errors. Manual fixes may be needed."
                )
                return 2
        else:
            print(f"Error: Expected output file {output_file} was not created.")
            return 1
    except subprocess.CalledProcessError as e:
        print(f"Error running test generator: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
