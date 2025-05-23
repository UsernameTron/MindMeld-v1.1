#!/usr/bin/env python3

import argparse
import importlib.util
import os
import re
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax

from packages.agents.claude_agents.agents.test_generator import TestGeneratorAgent

console = Console()


def import_module_from_path(file_path):
    """Import a module from a file path for inspection."""
    try:
        module_name = os.path.basename(file_path).replace(".py", "")
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        console.print(
            f"[yellow]Warning: Could not import {file_path} for inspection: {e}[/yellow]"
        )
        return None


def gather_fixtures(code_path):
    """Gather test fixtures that might be helpful for the tests."""
    fixtures = {}

    # Try to import the module to analyze it
    module = import_module_from_path(code_path)
    if module:
        # Look for any sample data, config, or test helpers
        for attr_name in dir(module):
            if attr_name.startswith("_"):
                continue

            attr = getattr(module, attr_name)

            # Add dictionaries that might be useful for testing
            if isinstance(attr, dict) and len(attr) > 0:
                fixtures[f"{attr_name}_fixture"] = attr

            # Add any constants that might be useful
            if isinstance(attr, (str, int, float, bool)) and attr_name.isupper():
                fixtures[f"{attr_name.lower()}_fixture"] = attr

    return fixtures


def enhance_tests(test_code, file_path):
    """
    Enhance the generated tests with proper import paths, common test patterns,
    and better organization.

    Args:
        test_code: The generated test code
        file_path: Path to the source file being tested

    Returns:
        Enhanced test code
    """
    # Parse module information from file path to fix imports
    module_name = os.path.basename(file_path).replace(".py", "")
    rel_path = os.path.relpath(file_path, "src").replace(".py", "")
    module_path = rel_path.replace(os.path.sep, ".")

    # Get a better capitalized version for class names
    module_name_capitalized = "".join(
        word.capitalize() for word in module_name.split("_")
    )

    # Fix imports by analyzing existing import statements
    import_pattern = re.compile(r"from\s+(\w+(?:\.\w+)*)\s+import\s+(.+?)(?:\n|$)")
    matches = import_pattern.findall(test_code)

    fixed_imports = []
    has_unittest = False

    # Add import for sys, os and path manipulation for proper test execution
    path_import = "import sys\nimport os\n# Add the src directory to the path\nsys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))\n"
    fixed_imports.append(path_import)

    # Check and fix import paths
    for imp_from, imp_what in matches:
        # Skip non-relative imports and special cases
        if imp_from in (
            "unittest",
            "mock",
            "pytest",
            "typing",
            "tempfile",
            "json",
            "os",
            "sys",
            "pathlib",
            "shutil",
        ):
            if imp_from == "unittest":
                has_unittest = True
            fixed_imports.append(f"from {imp_from} import {imp_what}")
            continue

        # Make proper import from src
        if not imp_from.startswith("src."):
            fixed_imports.append(f"from src.{imp_from} import {imp_what}")
        else:
            fixed_imports.append(f"from {imp_from} import {imp_what}")

    # Ensure unittest is imported
    if not has_unittest and "import unittest" not in test_code:
        fixed_imports.insert(1, "import unittest")

    # Try to extract the direct import of the module being tested
    direct_import = f"# Import the module being tested\nfrom src.{module_path} import *"
    fixed_imports.append(direct_import)

    # Replace all import statements with our fixed ones
    import_section = "\n".join(fixed_imports)

    # Remove existing imports
    test_code = re.sub(
        r"(import .+?\n|from .+? import .+?\n)+", "", test_code, flags=re.MULTILINE
    )

    # Add our fixed imports
    if test_code.startswith("import"):
        test_code = import_section + "\n\n" + test_code
    else:
        # Add imports after any initial comments
        comment_end = 0
        for line in test_code.split("\n"):
            if line.strip() and not line.strip().startswith("#"):
                break
            comment_end += len(line) + 1

        test_code = (
            test_code[:comment_end] + import_section + "\n\n" + test_code[comment_end:]
        )

    # Fix class naming - ensure consistent "Test" prefix + ModuleName pattern
    class_pattern = re.compile(r"class\s+Test(\w+)\(unittest\.TestCase\):")
    matches = class_pattern.findall(test_code)

    # Create a base test class if there are multiple test classes
    if len(matches) > 1:
        base_class_code = (
            f"\nclass Test{module_name_capitalized}Base(unittest.TestCase):\n"
        )
        base_class_code += "    def setUp(self):\n"
        base_class_code += '        """Set up test fixtures."""\n'
        base_class_code += "        pass\n\n"
        base_class_code += "    def tearDown(self):\n"
        base_class_code += '        """Clean up after tests."""\n'
        base_class_code += "        pass\n\n"

        # Add base class after imports
        import_end = test_code.find("\n\n", test_code.find("import"))
        if import_end == -1:
            import_end = len(test_code)
        test_code = (
            test_code[:import_end] + "\n" + base_class_code + test_code[import_end:]
        )

        # Update subclasses to inherit from the base class
        test_code = re.sub(
            r"class\s+Test(\w+)\(unittest\.TestCase\):",
            f"class Test\\1(Test{module_name_capitalized}Base):",
            test_code,
        )

    # Apply any module-specific templates
    test_code = apply_module_specific_templates(test_code, file_path)

    return test_code


def apply_module_specific_templates(test_code, file_path):
    """Apply specific test templates based on the module type."""

    # Template for file operations modules
    if any(
        keyword in file_path for keyword in ["file_operations", "io", "storage", "fs"]
    ):
        return enhance_file_operations_tests(test_code, file_path)

    # Template for authentication/user modules
    elif any(
        keyword in file_path for keyword in ["auth", "user", "permission", "security"]
    ):
        return enhance_auth_tests(test_code, file_path)

    # Template for API/model interaction modules
    elif any(
        keyword in file_path for keyword in ["api", "model", "llm", "client", "request"]
    ):
        return enhance_api_tests(test_code, file_path)

    # Default case - use general enhancements
    return test_code


def enhance_file_operations_tests(test_code, file_path):
    """Apply file operations specific test enhancements."""

    module_name = os.path.basename(file_path).replace(".py", "")

    # Add file operation specific imports
    file_imports = """import os
import tempfile
import shutil
import json
from pathlib import Path
from unittest import mock"""

    # Find where to insert the imports
    if "import unittest" in test_code:
        test_code = test_code.replace(
            "import unittest", f"import unittest\n{file_imports}"
        )

    # Add common file operation test patterns
    if "def setUp(self):" in test_code:
        setup_code = """    def setUp(self):
        \"\"\"Set up a temporary directory for file operations tests.\"\"\"
        self.temp_dir = tempfile.mkdtemp()

        # Create test files
        self.test_file_path = os.path.join(self.temp_dir, "test_file.txt")
        with open(self.test_file_path, 'w') as f:
            f.write("Test content")

        self.test_json_path = os.path.join(self.temp_dir, "test_file.json")
        test_data = {"name": "Test", "value": 42}
        with open(self.test_json_path, 'w') as f:
            json.dump(test_data, f)

    def tearDown(self):
        \"\"\"Clean up the temporary directory.\"\"\"
        shutil.rmtree(self.temp_dir)"""

        # Replace the basic setUp with our enhanced version
        test_code = re.sub(
            r"def setUp\(self\):.*?self\.instance = .*?\(\)",
            setup_code,
            test_code,
            flags=re.DOTALL,
        )

    # Add common test methods for file operations
    # This handles common file operations like read, write, exists
    common_tests = """
    def test_file_not_found(self):
        \"\"\"Test behavior when a file is not found.\"\"\"
        non_existent_path = os.path.join(self.temp_dir, "non_existent.txt")

        # Test with your module's functions that should handle missing files
        # Example: with self.assertRaises(FileNotFoundError):
        #     your_module.read_file(non_existent_path)
        self.assertFalse(os.path.exists(non_existent_path))

    def test_file_permissions(self):
        \"\"\"Test behavior with file permission issues.\"\"\"
        # Skip on Windows where chmod behaves differently
        if os.name == 'nt':
            self.skipTest("Skipping permission test on Windows")

        # Create a file with restricted permissions
        restricted_path = os.path.join(self.temp_dir, "restricted.txt")
        with open(restricted_path, 'w') as f:
            f.write("Restricted content")

        # Make file read-only
        os.chmod(restricted_path, 0o400)

        # Your permission-related tests here
        self.assertTrue(os.path.exists(restricted_path))
    """

    # Find where to add our common tests
    if "if __name__ == '__main__':" in test_code:
        test_code = test_code.replace(
            "if __name__ == '__main__':", f"{common_tests}\nif __name__ == '__main__':"
        )
    else:
        test_code = test_code + common_tests

    return test_code


def enhance_auth_tests(test_code, file_path):
    """Apply authentication specific test enhancements."""

    # Add auth specific imports
    auth_imports = """import unittest.mock as mock
import json
import jwt
from datetime import datetime, timedelta"""

    # Find where to insert the imports
    if "import unittest" in test_code:
        test_code = test_code.replace(
            "import unittest", f"import unittest\n{auth_imports}"
        )

    # Add auth-related fixtures
    auth_fixtures = """
    def setUp(self):
        \"\"\"Set up test fixtures for authentication tests.\"\"\"
        # Mock user data
        self.test_user = {
            "id": "user123",
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": "hashed_password",
            "roles": ["user"]
        }

        # Mock JWT token data
        self.test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIiwiZXhwIjoxNjE2MTc5MjAwfQ.signature"

        # Mock admin user
        self.admin_user = {
            "id": "admin456",
            "username": "adminuser",
            "email": "admin@example.com",
            "password_hash": "admin_hashed_password",
            "roles": ["admin"]
        }
    """

    # Replace the basic setUp with our enhanced version
    if "def setUp(self):" in test_code:
        test_code = re.sub(
            r"def setUp\(self\):.*?(def test_|$)",
            f"{auth_fixtures}\n    def test_",
            test_code,
            flags=re.DOTALL,
        )
    else:
        # If no setUp, add it after the class definition
        class_pattern = r"class Test\w+\(unittest\.TestCase\):"
        match = re.search(class_pattern, test_code)
        if match:
            class_def_end = match.end()
            test_code = (
                test_code[:class_def_end] + auth_fixtures + test_code[class_def_end:]
            )

    # Add common auth test methods
    common_tests = """
    def test_invalid_token(self):
        \"\"\"Test behavior with invalid authentication token.\"\"\"
        invalid_token = "invalid.token.format"

        # Example test with a mock
        with mock.patch('jwt.decode', side_effect=jwt.InvalidTokenError):
            # Your module's token validation function would go here
            # Example: with self.assertRaises(AuthenticationError):
            #     your_module.validate_token(invalid_token)
            pass

    def test_expired_token(self):
        \"\"\"Test behavior with expired token.\"\"\"
        # Create expired token
        expired_time = datetime.now() - timedelta(days=1)
        expired_payload = {
            "sub": "user123",
            "exp": int(expired_time.timestamp())
        }

        with mock.patch('jwt.decode', side_effect=jwt.ExpiredSignatureError):
            # Example: with self.assertRaises(AuthenticationError):
            #     your_module.validate_token("expired.token.here")
            pass
    """

    # Add common auth test methods
    if "if __name__ == '__main__':" in test_code:
        test_code = test_code.replace(
            "if __name__ == '__main__':", f"{common_tests}\nif __name__ == '__main__':"
        )
    else:
        test_code = test_code + common_tests

    return test_code


def enhance_api_tests(test_code, file_path):
    """Apply API/model interaction specific test enhancements."""

    # Add API/model specific imports
    api_imports = """import unittest.mock as mock
import json
import requests
from unittest.mock import MagicMock, patch"""

    # Find where to insert the imports
    if "import unittest" in test_code:
        test_code = test_code.replace(
            "import unittest", f"import unittest\n{api_imports}"
        )

    # Add API-related setup
    api_setup = """
    def setUp(self):
        \"\"\"Set up test fixtures for API tests.\"\"\"
        # Mock API response data
        self.mock_api_response = {
            "id": "resp123",
            "status": "success",
            "data": {
                "results": [{"name": "Item 1"}, {"name": "Item 2"}]
            }
        }

        # Mock error response
        self.mock_error_response = {
            "status": "error",
            "error": {
                "code": 400,
                "message": "Bad request"
            }
        }

        # Setup request patching
        self.requests_patcher = patch('requests.request')
        self.mock_request = self.requests_patcher.start()

        # Default mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_api_response
        mock_response.text = json.dumps(self.mock_api_response)
        self.mock_request.return_value = mock_response

    def tearDown(self):
        \"\"\"Clean up after tests.\"\"\"
        self.requests_patcher.stop()
    """

    # Replace the basic setUp with our enhanced version
    if "def setUp(self):" in test_code:
        test_code = re.sub(
            r"def setUp\(self\):.*?(def tearDown\(self\):.*?)??(def test_|$)",
            f"{api_setup}\n    def test_",
            test_code,
            flags=re.DOTALL,
        )
    else:
        # If no setUp, add it after the class definition
        class_pattern = r"class Test\w+\(unittest\.TestCase\):"
        match = re.search(class_pattern, test_code)
        if match:
            class_def_end = match.end()
            test_code = (
                test_code[:class_def_end] + api_setup + test_code[class_def_end:]
            )

    # Add common API test methods
    common_tests = """
    def test_api_error_handling(self):
        \"\"\"Test how API errors are handled.\"\"\"
        # Configure mock to return an error
        mock_error = MagicMock()
        mock_error.status_code = 400
        mock_error.json.return_value = self.mock_error_response
        mock_error.text = json.dumps(self.mock_error_response)
        self.mock_request.return_value = mock_error

        # Your API call would go here
        # Example: with self.assertRaises(APIError):
        #     your_module.api_function("arg1")

    def test_api_timeout(self):
        \"\"\"Test behavior when API times out.\"\"\"
        # Configure mock to simulate a timeout
        self.mock_request.side_effect = requests.Timeout("Connection timed out")

        # Your API call would go here
        # Example: with self.assertRaises(TimeoutError):
        #     your_module.api_function("arg1")

    def test_successful_api_call(self):
        \"\"\"Test successful API interaction.\"\"\"
        # Setup mock for success case
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"result": "success", "data": [1, 2, 3]}
        self.mock_request.return_value = mock_success

        # Your API call would go here
        # result = your_module.api_function("arg1")
        # self.assertEqual(result, [1, 2, 3])
    """

    # Add common API test methods
    if "if __name__ == '__main__':" in test_code:
        test_code = test_code.replace(
            "if __name__ == '__main__':", f"{common_tests}\nif __name__ == '__main__':"
        )
    else:
        test_code = test_code + common_tests

    return test_code


def main():
    parser = argparse.ArgumentParser(description="Generate tests for Python code")
    parser.add_argument("--path", "-p", default="src/utils", help="Path to scan")
    parser.add_argument(
        "--output", "-o", default="tests/generated", help="Output directory"
    )
    parser.add_argument(
        "--framework",
        "-f",
        default="pytest",
        choices=["pytest", "unittest"],
        help="Test framework to use",
    )
    parser.add_argument(
        "--single",
        "-s",
        action="store_true",
        help="Process a single file instead of directory",
    )
    parser.add_argument(
        "--enhance",
        "-e",
        action="store_true",
        help="Enhance tests with better setup and assertions",
    )
    parser.add_argument(
        "--template",
        "-t",
        choices=["file", "auth", "api", "general"],
        help="Apply a specific template to generated tests",
    )
    parser.add_argument(
        "--priority",
        "-P",
        choices=["high", "medium", "low"],
        default="medium",
        help="Process only modules with specified priority",
    )
    parser.add_argument(
        "--debug",
        "-d",
        action="store_true",
        help="Run CodeDebugAgent on generated tests to fix issues",
    )
    parser.add_argument(
        "--priority-modules",
        nargs="+",
        help="List of high-priority module names to focus on",
    )
    args = parser.parse_args()

    # Initialize the agent
    agent = TestGeneratorAgent(test_framework=args.framework)

    # Load debug agent if requested
    debug_agent = None
    if args.debug:
        try:
            from packages.agents.claude_agents.agents.code_debug import CodeDebugAgent

            debug_agent = CodeDebugAgent()
            console.print(
                "[bold green]Loaded CodeDebugAgent for test improvement[/bold green]"
            )
        except ImportError:
            console.print(
                "[yellow]Warning: CodeDebugAgent not available. Debug functionality disabled.[/yellow]"
            )

    # Handle priority modules filtering
    priority_modules = []
    if args.priority_modules:
        priority_modules = args.priority_modules
        console.print(
            f"[bold]Focusing on {len(priority_modules)} priority modules[/bold]"
        )

    if args.single:
        # Process a single file
        with open(args.path, "r") as f:
            code = f.read()

        # Check if this is a priority module when filtering is enabled
        if priority_modules and not any(
            module in args.path for module in priority_modules
        ):
            console.print(f"[yellow]Skipping non-priority module: {args.path}[/yellow]")
            return

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Generating tests...", total=1)

            # Gather fixtures from the source file
            fixtures = gather_fixtures(args.path) if args.enhance else {}

            # Process the file
            result = agent.process(
                {"code": code, "file_path": args.path, "fixtures": fixtures}
            )

            progress.update(task, advance=1)

        # Enhance the generated tests if requested
        test_code = result["test_code"]
        if args.enhance:
            test_code = enhance_tests(test_code, args.path)

            # Apply specific template if requested
            if args.template:
                if args.template == "file":
                    test_code = enhance_file_operations_tests(test_code, args.path)
                elif args.template == "auth":
                    test_code = enhance_auth_tests(test_code, args.path)
                elif args.template == "api":
                    test_code = enhance_api_tests(test_code, args.path)

        # Create output directory if it doesn't exist
        os.makedirs(args.output, exist_ok=True)

        # Generate output filename
        base_name = os.path.basename(args.path)
        output_file = os.path.join(args.output, f"test_{base_name}")

        # Write test file
        with open(output_file, "w") as f:
            f.write(test_code)

        # Run debug agent if requested
        if debug_agent:
            console.print("[cyan]Running CodeDebugAgent to improve tests...[/cyan]")
            try:
                debug_result = debug_agent.process(
                    {
                        "code": test_code,
                        "file_path": output_file,
                        "source_file": args.path,
                    }
                )

                if debug_result.get("fixed_code"):
                    # Write the fixed version
                    with open(output_file, "w") as f:
                        f.write(debug_result["fixed_code"])

                    console.print(
                        f"[bold green]Debug agent fixed {debug_result.get('issues_fixed', 0)} issues[/bold green]"
                    )
            except Exception as e:
                console.print(
                    f"[yellow]Warning: Debug agent encountered an error: {str(e)}[/yellow]"
                )

        # Report results
        console.print(
            Panel.fit(
                f"[bold green]Generated test file:[/] {output_file}\n"
                f"[bold yellow]Estimated coverage:[/] {result['coverage_estimate']:.1f}%\n"
                f"[bold]Untested paths:[/] {len(result['untested_paths'])}"
            )
        )

        # Show preview
        syntax = Syntax(test_code[:1000] + "\n...", "python", theme="monokai")
        console.print(Panel(syntax, title="Test Preview", border_style="blue"))

        # Show untested paths if any
        if result["untested_paths"]:
            console.print("\n[bold yellow]Untested Paths:[/]")
            for path in result["untested_paths"]:
                console.print(f"  • {path}")
    else:
        # Process a directory
        file_count = 0
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Scanning directory...", total=None)

            for root, _, files in os.walk(args.path):
                py_files = [f for f in files if f.endswith(".py")]

                # Apply priority filtering if requested
                if priority_modules:
                    py_files = [
                        f
                        for f in py_files
                        if any(module in f for module in priority_modules)
                    ]
                    if not py_files:
                        continue

                progress.update(task, total=len(py_files), completed=0)

                for file in py_files:
                    file_path = os.path.join(root, file)
                    progress.update(task, description=f"[cyan]Processing {file}")

                    try:
                        with open(file_path, "r") as f:
                            code = f.read()

                        # Gather fixtures from the source file
                        fixtures = gather_fixtures(file_path) if args.enhance else {}

                        # Process the file
                        result = agent.process(
                            {"code": code, "file_path": file_path, "fixtures": fixtures}
                        )

                        # Enhance the generated tests if requested
                        test_code = result["test_code"]
                        if args.enhance:
                            test_code = enhance_tests(test_code, file_path)

                        # Create relative directory structure in output
                        rel_path = os.path.relpath(root, args.path)
                        output_dir = os.path.join(args.output, rel_path)
                        os.makedirs(output_dir, exist_ok=True)

                        # Generate output filename
                        output_file = os.path.join(output_dir, f"test_{file}")

                        # Write test file
                        with open(output_file, "w") as f:
                            f.write(test_code)

                        # Run debug agent if requested
                        if debug_agent:
                            try:
                                debug_result = debug_agent.process(
                                    {
                                        "code": test_code,
                                        "file_path": output_file,
                                        "source_file": file_path,
                                    }
                                )

                                if debug_result.get("fixed_code"):
                                    # Write the fixed version
                                    with open(output_file, "w") as f:
                                        f.write(debug_result["fixed_code"])
                            except Exception as e:
                                console.print(
                                    f"[yellow]Warning: Debug agent error for {file}: {str(e)}[/yellow]"
                                )

                        file_count += 1
                        progress.update(task, advance=1)
                    except Exception as e:
                        console.print(
                            f"Error processing {file_path}: [red]{str(e)}[/red]"
                        )
                        progress.update(task, advance=1)

        console.print(
            f"\n[bold green]Success![/] Generated [bold]{file_count}[/bold] test files in [bold]{args.output}[/bold]"
        )


if __name__ == "__main__":
    main()
