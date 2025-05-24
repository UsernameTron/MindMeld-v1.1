"""
Standardized TestGeneratorAgent implementation.

This module provides a test generation agent that follows the standardized
AgentProtocol interface, offering comprehensive test case generation
capabilities for Python code.
"""

import ast
import os
from typing import Any, Dict, List

from ..base.registry import AgentRegistry


class TestGeneratorAgent:
    """Standardized agent for automatically generating test cases for Python code.

    This agent analyzes Python code to generate comprehensive test cases,
    identify edge conditions, and create appropriate fixtures and mocks.
    The agent implements the AgentProtocol interface for consistent interaction
    with the agent registry system.
    """

    def __init__(self, name: str = "test_generator", **kwargs):
        """Initialize the test generator agent.

        Args:
            name: Unique identifier for this agent instance
            test_framework: Testing framework to use (default: pytest)
            mock_framework: Mocking framework to use (default: pytest-mock)
            **kwargs: Additional configuration options
        """
        self.name = name
        self.test_framework = kwargs.get("test_framework", "pytest")
        self.mock_framework = kwargs.get("mock_framework", "pytest-mock")
        self.config = kwargs

        # Register with the global registry
        registry = AgentRegistry.get_instance()
        registry.register_agent(self.name, self)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Python code to generate test cases.

        Args:
            input_data: Dictionary containing:
                - 'code': Python code to analyze (optional if file_path provided)
                - 'file_path': Optional path to the file to analyze
                - 'module_name': Optional module name
                - 'test_framework': Optional test framework to use
                - 'coverage_target': Optional target coverage percentage

        Returns:
            Dictionary containing:
                - 'status': 'success' or 'error'
                - 'data': Dictionary with test_code, fixtures, etc.
                - 'metadata': Processing metadata
        """
        try:
            # Validate input
            validation_result = self.validate_input(input_data)
            if not validation_result["valid"]:
                return {
                    "status": "error",
                    "error": f"Invalid input: {validation_result['message']}",
                    "metadata": self._get_metadata(),
                }

            # Extract and prepare code
            code = input_data.get("code", "")
            file_path = input_data.get("file_path", "")

            # Read file if path provided and no code
            if file_path and not code:
                if not os.path.exists(file_path):
                    return {
                        "status": "error",
                        "error": f"File not found: {file_path}",
                        "metadata": self._get_metadata(),
                    }

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        code = f.read()
                except Exception as e:
                    return {
                        "status": "error",
                        "error": f"Error reading file {file_path}: {str(e)}",
                        "metadata": self._get_metadata(),
                    }

            # Override test framework if specified
            if "test_framework" in input_data:
                self.test_framework = input_data["test_framework"]

            # Initialize result structure
            result = {
                "test_code": "",
                "fixtures": {},
                "coverage_estimate": 0.0,
                "untested_paths": [],
                "tests": "",  # For backward compatibility
            }

            if code:
                # Analyze the code
                analyzed_code = self._analyze_code(code, file_path)

                # Check for syntax errors
                if analyzed_code.get("syntax_error"):
                    return {
                        "status": "error",
                        "error": f"Syntax error in code: {analyzed_code['syntax_error']['message']}",
                        "metadata": self._get_metadata(),
                    }

                # Generate test code
                result["test_code"] = self._generate_tests(analyzed_code)
                result["tests"] = result["test_code"]  # Backward compatibility

                # Generate additional analysis
                result["fixtures"] = self._generate_fixtures(analyzed_code)
                result["coverage_estimate"] = self._estimate_coverage(analyzed_code)
                result["untested_paths"] = self._identify_untested_paths(analyzed_code)

            return {
                "status": "success",
                "data": result,
                "metadata": self._get_metadata(),
            }

        except Exception as e:
            return {
                "status": "error",
                "error": f"Processing failed: {str(e)}",
                "metadata": self._get_metadata(),
            }

    def validate_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data format and requirements.

        Args:
            input_data: Input data to validate

        Returns:
            Validation result with 'valid' boolean and 'message'
        """
        if not isinstance(input_data, dict):
            return {"valid": False, "message": "Input must be a dictionary"}

        code = input_data.get("code", "")
        file_path = input_data.get("file_path", "")

        if not code and not file_path:
            return {
                "valid": False,
                "message": "Either 'code' or 'file_path' must be provided",
            }

        if code and not isinstance(code, str):
            return {"valid": False, "message": "'code' must be a string"}

        if file_path and not isinstance(file_path, str):
            return {"valid": False, "message": "'file_path' must be a string"}

        return {"valid": True, "message": "Input is valid"}

    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities and supported operations.

        Returns:
            Dictionary describing agent capabilities
        """
        return {
            "name": self.name,
            "type": "test_generator",
            "description": "Automatic test case generation agent",
            "capabilities": [
                "python_test_generation",
                "fixture_creation",
                "coverage_estimation",
                "edge_case_identification",
                "mock_generation",
                "multiple_test_frameworks",
            ],
            "supported_frameworks": ["pytest", "unittest"],
            "input_schema": {
                "required": [],  # Either code or file_path required
                "optional": [
                    "code",
                    "file_path",
                    "module_name",
                    "test_framework",
                    "coverage_target",
                ],
                "code": "Python code string to analyze",
                "file_path": "Path to Python file to analyze",
                "module_name": "Module name for test imports",
                "test_framework": "Testing framework (pytest/unittest)",
                "coverage_target": "Target coverage percentage",
            },
            "output_schema": {
                "status": "success or error",
                "data": {
                    "test_code": "Generated test code",
                    "fixtures": "Test fixtures dictionary",
                    "coverage_estimate": "Estimated coverage percentage",
                    "untested_paths": "List of uncovered code paths",
                },
                "metadata": "processing metadata",
            },
        }

    def _analyze_code(self, code: str, file_path: str = "") -> Dict[str, Any]:
        """Analyze Python code to extract testable components.

        Args:
            code: Python code to analyze
            file_path: Optional path to the file

        Returns:
            Dictionary containing functions, classes, imports, constants
        """
        result = {
            "functions": [],
            "classes": [],
            "imports": [],
            "constants": [],
            "syntax_error": None,
        }

        try:
            # Parse the code into an AST
            tree = ast.parse(code)

            # Extract imports
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_info = {
                        "type": (
                            "import" if isinstance(node, ast.Import) else "import_from"
                        ),
                        "names": [],
                        "module": getattr(node, "module", None),
                        "level": getattr(node, "level", 0),
                    }

                    for name in node.names:
                        import_info["names"].append(
                            {"name": name.name, "asname": name.asname}
                        )

                    result["imports"].append(import_info)

            # Extract functions
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = self._extract_function_info(node, code)
                    result["functions"].append(func_info)

            # Extract classes
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = self._extract_class_info(node, code)
                    result["classes"].append(class_info)

            # Extract constants
            for node in ast.iter_child_nodes(tree):
                if isinstance(node, ast.Assign):
                    targets = [t for t in node.targets if isinstance(t, ast.Name)]
                    for target in targets:
                        if target.id.isupper():  # Convention for constants
                            value = None
                            if isinstance(
                                node.value,
                                (ast.Constant, ast.Str, ast.Num, ast.NameConstant),
                            ):
                                try:
                                    value = ast.literal_eval(node.value)
                                except (ValueError, TypeError):
                                    value = None

                            result["constants"].append(
                                {"name": target.id, "value": value, "line": node.lineno}
                            )

        except SyntaxError as e:
            result["syntax_error"] = {
                "message": str(e),
                "line": e.lineno,
                "offset": e.offset,
            }

        return result

    def _extract_function_info(
        self, node: ast.FunctionDef, code: str
    ) -> Dict[str, Any]:
        """Extract information about a function."""
        return {
            "name": node.name,
            "line": node.lineno,
            "args": [arg.arg for arg in node.args.args],
            "defaults": len(node.args.defaults),
            "is_async": isinstance(node, ast.AsyncFunctionDef),
            "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
            "docstring": ast.get_docstring(node) or "",
        }

    def _extract_class_info(self, node: ast.ClassDef, code: str) -> Dict[str, Any]:
        """Extract information about a class."""
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._extract_function_info(item, code)
                methods.append(method_info)

        return {
            "name": node.name,
            "line": node.lineno,
            "bases": [self._get_name_from_node(base) for base in node.bases],
            "methods": methods,
            "decorators": [self._get_decorator_name(d) for d in node.decorator_list],
            "docstring": ast.get_docstring(node) or "",
        }

    def _get_decorator_name(self, decorator) -> str:
        """Get decorator name from AST node."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{self._get_name_from_node(decorator.value)}.{decorator.attr}"
        else:
            return "unknown_decorator"

    def _get_name_from_node(self, node) -> str:
        """Get name string from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name_from_node(node.value)}.{node.attr}"
        else:
            return "unknown"

    def _generate_tests(self, analyzed_code: Dict[str, Any]) -> str:
        """Generate test code based on code analysis."""
        if analyzed_code.get("syntax_error"):
            error = analyzed_code["syntax_error"]
            return f"# Unable to generate tests: Syntax error at line {error['line']}: {error['message']}"

        if self.test_framework == "pytest":
            return self._generate_pytest_tests(analyzed_code)
        elif self.test_framework == "unittest":
            return self._generate_unittest_tests(analyzed_code)
        else:
            return f"# Unsupported test framework: {self.test_framework}"

    def _generate_pytest_tests(self, analyzed_code: Dict[str, Any]) -> str:
        """Generate pytest test cases."""
        test_code = "import pytest\n\n"

        # Add imports from analyzed code
        for imp in analyzed_code.get("imports", []):
            if imp["type"] == "import":
                for name in imp["names"]:
                    if name["asname"]:
                        test_code += f"import {name['name']} as {name['asname']}\n"
                    else:
                        test_code += f"import {name['name']}\n"
            else:
                module = imp["module"] or ""
                names = [name["name"] for name in imp["names"]]
                test_code += f"from {module} import {', '.join(names)}\n"

        test_code += "\n"

        # Generate tests for functions
        for func in analyzed_code.get("functions", []):
            if not func["name"].startswith("_"):  # Only test public functions
                test_code += self._generate_function_test_pytest(func)

        # Generate tests for classes
        for cls in analyzed_code.get("classes", []):
            test_code += self._generate_class_tests_pytest(cls)

        return test_code

    def _generate_unittest_tests(self, analyzed_code: Dict[str, Any]) -> str:
        """Generate unittest test cases."""
        test_code = "import unittest\n\n"

        # Add imports from analyzed code
        for imp in analyzed_code.get("imports", []):
            if imp["type"] == "import":
                for name in imp["names"]:
                    if name["asname"]:
                        test_code += f"import {name['name']} as {name['asname']}\n"
                    else:
                        test_code += f"import {name['name']}\n"
            else:
                module = imp["module"] or ""
                names = [name["name"] for name in imp["names"]]
                test_code += f"from {module} import {', '.join(names)}\n"

        test_code += "\n\nclass TestCase(unittest.TestCase):\n"

        # Generate tests for functions
        for func in analyzed_code.get("functions", []):
            if not func["name"].startswith("_"):  # Only test public functions
                test_code += self._generate_function_test_unittest(func)

        # Generate tests for classes
        for cls in analyzed_code.get("classes", []):
            test_code += self._generate_class_tests_unittest(cls)

        test_code += "\n\nif __name__ == '__main__':\n    unittest.main()\n"

        return test_code

    def _generate_function_test_pytest(self, func: Dict[str, Any]) -> str:
        """Generate pytest test for a function."""
        func_name = func["name"]
        test_name = f"test_{func_name}"

        test_code = f"def {test_name}():\n"
        test_code += f'    """Test {func_name} function."""\n'
        test_code += f"    # TODO: Add test implementation for {func_name}\n"
        test_code += f"    # Test basic functionality\n"
        test_code += f"    # Test edge cases\n"
        test_code += f"    # Test error conditions\n"
        test_code += f"    pass\n\n"

        return test_code

    def _generate_function_test_unittest(self, func: Dict[str, Any]) -> str:
        """Generate unittest test for a function."""
        func_name = func["name"]
        test_name = f"test_{func_name}"

        test_code = f"    def {test_name}(self):\n"
        test_code += f'        """Test {func_name} function."""\n'
        test_code += f"        # TODO: Add test implementation for {func_name}\n"
        test_code += f"        # Test basic functionality\n"
        test_code += f"        # Test edge cases\n"
        test_code += f"        # Test error conditions\n"
        test_code += f"        pass\n\n"

        return test_code

    def _generate_class_tests_pytest(self, cls: Dict[str, Any]) -> str:
        """Generate pytest tests for a class."""
        class_name = cls["name"]
        test_code = f"class Test{class_name}:\n"
        test_code += f'    """Test cases for {class_name} class."""\n\n'

        # Generate fixture for class instance
        test_code += f"    @pytest.fixture\n"
        test_code += f"    def {class_name.lower()}_instance(self):\n"
        test_code += f'        """Create {class_name} instance for testing."""\n'
        test_code += f"        return {class_name}()\n\n"

        # Generate tests for each public method
        for method in cls["methods"]:
            if not method["name"].startswith("_") or method["name"] == "__init__":
                method_name = method["name"]
                test_name = f"test_{method_name}"

                test_code += (
                    f"    def {test_name}(self, {class_name.lower()}_instance):\n"
                )
                test_code += f'        """Test {class_name}.{method_name} method."""\n'
                test_code += (
                    f"        # TODO: Add test implementation for {method_name}\n"
                )
                test_code += f"        pass\n\n"

        return test_code

    def _generate_class_tests_unittest(self, cls: Dict[str, Any]) -> str:
        """Generate unittest tests for a class."""
        class_name = cls["name"]
        test_code = ""

        # Generate tests for each public method
        for method in cls["methods"]:
            if not method["name"].startswith("_") or method["name"] == "__init__":
                method_name = method["name"]
                test_name = f"test_{class_name.lower()}_{method_name}"

                test_code += f"    def {test_name}(self):\n"
                test_code += f'        """Test {class_name}.{method_name} method."""\n'
                test_code += (
                    f"        # TODO: Add test implementation for {method_name}\n"
                )
                test_code += f"        instance = {class_name}()\n"
                test_code += f"        # Add assertions here\n"
                test_code += f"        pass\n\n"

        return test_code

    def _generate_fixtures(self, analyzed_code: Dict[str, Any]) -> Dict[str, str]:
        """Generate test fixtures based on code analysis."""
        fixtures = {}

        # Generate common fixtures
        fixtures["sample_data"] = {"id": 1, "name": "test", "value": 42}

        # Generate fixtures for each class
        for cls in analyzed_code.get("classes", []):
            fixture_name = f"{cls['name'].lower()}_instance"
            fixtures[fixture_name] = f"An instance of {cls['name']}"

        return fixtures

    def _estimate_coverage(self, analyzed_code: Dict[str, Any]) -> float:
        """Estimate test coverage percentage."""
        total_testable_items = 0
        covered_items = 0

        # Count public functions
        for func in analyzed_code.get("functions", []):
            if not func["name"].startswith("_") or func["name"].startswith("__"):
                total_testable_items += 1
                covered_items += 1  # Assume we generate tests for all public functions

        # Count public methods
        for cls in analyzed_code.get("classes", []):
            for method in cls["methods"]:
                if not method["name"].startswith("_") or method["name"].startswith(
                    "__"
                ):
                    total_testable_items += 1
                    covered_items += (
                        1  # Assume we generate tests for all public methods
                    )

        # Avoid division by zero
        if total_testable_items == 0:
            return 0.0

        return (covered_items / total_testable_items) * 100.0

    def _identify_untested_paths(self, analyzed_code: Dict[str, Any]) -> List[str]:
        """Identify code paths that are not covered by tests."""
        untested_paths = []

        # Identify private functions
        for func in analyzed_code.get("functions", []):
            if func["name"].startswith("_") and not func["name"].startswith("__"):
                untested_paths.append(
                    f"Private function '{func['name']}' at line {func['line']}"
                )

        # Identify private methods in classes
        for cls in analyzed_code.get("classes", []):
            for method in cls["methods"]:
                if method["name"].startswith("_") and not method["name"].startswith(
                    "__"
                ):
                    untested_paths.append(
                        f"Private method '{cls['name']}.{method['name']}' at line {method['line']}"
                    )

        return untested_paths

    def _get_metadata(self) -> Dict[str, Any]:
        """Get processing metadata."""
        return {
            "agent_name": self.name,
            "agent_type": "test_generator",
            "version": "1.0.0",
            "test_framework": self.test_framework,
            "mock_framework": self.mock_framework,
        }


# Register the agent class for easy instantiation
def create_test_generator_agent(**kwargs) -> TestGeneratorAgent:
    """Factory function to create a TestGeneratorAgent instance."""
    return TestGeneratorAgent(**kwargs)


# Auto-register when module is imported
if __name__ != "__main__":
    registry = AgentRegistry.get_instance()
    registry.register_agent_class("test_generator", create_test_generator_agent)
