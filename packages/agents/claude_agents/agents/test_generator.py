import ast
from typing import Any, Dict, List

from ..agents.base import Agent


class TestGeneratorAgent(Agent):
    """Agent for automatically generating test cases for Python code.

    This agent analyzes Python code to generate comprehensive test cases,
    identify edge conditions, and create appropriate fixtures and mocks.
    """

    def __init__(self, **kwargs):
        """Initialize the test generator agent.

        Args:
            test_framework: Testing framework to use (default: pytest)
            mock_framework: Mocking framework to use (default: pytest-mock)
            **kwargs: Additional arguments to pass to the base Agent
        """
        super().__init__(**kwargs)
        self.test_framework = kwargs.get("test_framework", "pytest")
        self.mock_framework = kwargs.get("mock_framework", "pytest-mock")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process Python code to generate test cases.

        Args:
            input_data: Dictionary containing:
                - 'code': Python code to analyze
                - 'file_path': Optional path to the file
                - 'module_name': Optional module name
                - 'test_framework': Optional test framework to use
                - 'coverage_target': Optional target coverage percentage

        Returns:
            Dictionary containing:
                - 'status': "success" or "error"
                - 'data': Dictionary with test code, fixtures, etc. or
                - 'error': Error information if status is "error"
        """
        try:
            # Initialize result structure
            result = {
                "test_code": "",
                "fixtures": {},
                "coverage_estimate": 0.0,
                "untested_paths": [],
            }

            # Store input in history
            self.add_to_history({"role": "user", "content": str(input_data)})

            # Extract inputs
            code = input_data.get("code", "")
            file_path = input_data.get("file_path", "")

            # Check if file exists if a path was provided
            if file_path and not code:
                import os

                if not os.path.exists(file_path):
                    return {
                        "status": "error",
                        "error": {"message": f"File not found: {file_path}"},
                    }
                # Read the file content
                try:
                    with open(file_path, "r") as f:
                        code = f.read()
                except Exception as e:
                    return {
                        "status": "error",
                        "error": {
                            "message": f"Error reading file {file_path}: {str(e)}"
                        },
                    }

            # Override test framework if specified
            if "test_framework" in input_data:
                self.test_framework = input_data["test_framework"]

            # If we have code, generate tests
            if code:
                try:
                    # Use the API client to generate tests
                    prompt = f"Generate tests for the following code:\n\n{code}"
                    messages = [{"role": "user", "content": prompt}]

                    # Use the correct method from the base Agent class
                    response = self._call_claude(messages)

                    # Extract the test code from the API response
                    if response and hasattr(response, "content"):
                        # Extract content from structured response
                        result["test_code"] = response.content[0].text
                    elif isinstance(response, dict) and "output" in response:
                        # Handle MockClaudeAPIClient format in tests
                        result["test_code"] = response["output"]

                    # Add tests key for backward compatibility
                    result["tests"] = result["test_code"]

                except Exception as e:
                    # Handle API-specific errors
                    return {
                        "status": "error",
                        "error": {"message": f"LLM connection failed: {str(e)}"},
                    }

                # Generate additional information based on code analysis
                analyzed_code = self._analyze_code(code, file_path)
                result["fixtures"] = self._generate_fixtures(analyzed_code)
                result["coverage_estimate"] = self._estimate_coverage(analyzed_code)
                result["untested_paths"] = self._identify_untested_paths(analyzed_code)

            # Store result in history
            self.add_to_history({"role": "assistant", "content": str(result)})

            # Ensure result always contains a status key
            return {"status": "success", "data": result}
        except Exception as e:
            # Handle any unexpected exceptions
            error_message = str(e)
            self.add_to_history(
                {"role": "assistant", "content": f"Error: {error_message}"}
            )
            return {"status": "error", "error": {"message": error_message}}

    def _analyze_code(
        self, code: str, file_path: str = ""
    ) -> Dict[str, Any]:  # noqa: C901
        """
        Analyze Python code to extract testable components.

        Args:
            code: Python code to analyze
            file_path: Optional path to the file

        Returns:
            Dictionary containing:
                - 'functions': List of functions with parameters, return types, etc.
                - 'classes': List of classes with methods, attributes, etc.
                - 'imports': List of imports needed for testing
                - 'constants': List of constants that might be needed for tests
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
                            # Get the constant value if it's a literal
                            value = None
                            if isinstance(
                                node.value, (ast.Str, ast.Num, ast.NameConstant)
                            ):
                                value = ast.literal_eval(node.value)

                            result["constants"].append(
                                {"name": target.id, "value": value, "line": node.lineno}
                            )

        except SyntaxError as e:
            # Handle syntax errors gracefully
            result["syntax_error"] = {
                "message": str(e),
                "line": e.lineno,
                "offset": e.offset,
            }

        return result

    def _generate_tests(self, analyzed_code: Dict[str, Any]) -> str:
        """Generate test code based on code analysis."""
        if "syntax_error" in analyzed_code:
            return f"# Unable to generate tests: Syntax error at line {analyzed_code['syntax_error']['line']}"

        if self.test_framework == "pytest":
            return self._generate_pytest_tests(analyzed_code)
        elif self.test_framework == "unittest":
            return self._generate_unittest_tests(analyzed_code)
        else:
            return f"# Unsupported test framework: {self.test_framework}"

    def _generate_fixtures(self, analyzed_code: Dict[str, Any]) -> Dict[str, str]:
        """Generate test fixtures based on code analysis."""
        fixtures = {}

        # Generate fixtures for common data types
        fixtures["sample_data"] = {"id": 1, "name": "test", "value": 42}

        # Generate fixtures for each class if needed
        for cls in analyzed_code.get("classes", []):
            fixture_name = f"{cls['name'].lower()}_instance"
            fixtures[fixture_name] = f"An instance of {cls['name']}"

        return fixtures

    def _estimate_coverage(self, analyzed_code: Dict[str, Any]) -> float:
        """Estimate test coverage percentage."""
        total_testable_items = 0
        covered_items = 0

        # Count functions
        for func in analyzed_code.get("functions", []):
            if not func["name"].startswith("_") or func["name"].startswith("__"):
                total_testable_items += 1
                covered_items += (
                    1  # Assume we're generating tests for all public functions
                )

        # Count methods
        for cls in analyzed_code.get("classes", []):
            for method in cls["methods"]:
                if not method["name"].startswith("_") or method["name"].startswith(
                    "__"
                ):
                    total_testable_items += 1
                    covered_items += (
                        1  # Assume we're generating tests for all public methods
                    )

        # Avoid division by zero
        if total_testable_items == 0:
            return 0.0

        return (covered_items / total_testable_items) * 100.0

    def _identify_untested_paths(self, analyzed_code: Dict[str, Any]) -> List[str]:
        """Identify code paths that are not covered by tests."""
        untested_paths = []

        # In a real implementation, this would perform more sophisticated analysis
        # of conditional branches, loops, and exception handlers

        # For now, just mention any private methods that won't be directly tested
        for func in analyzed_code.get("functions", []):
            if func["name"].startswith("_") and not func["name"].startswith("__"):
                untested_paths.append(
                    f"Private function {func['name']!r} at line {func['line']}"
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

    def _extract_function_info(  # noqa: C901
        self, node: ast.FunctionDef, code: str
    ) -> Dict[str, Any]:
        """Extract detailed information about a function."""
        # Get function arguments
        args = []
        for arg in node.args.args:
            arg_info = {"name": arg.arg, "annotation": None}

            # Try to get type annotation
            if arg.annotation:
                arg_info["annotation"] = ast.unparse(arg.annotation)

            args.append(arg_info)

        # Get return type annotation
        returns = None
        if node.returns:
            returns = ast.unparse(node.returns)

        # Get function docstring
        docstring = ast.get_docstring(node)

        # Identify if the function is a method
        is_method = False
        if len(args) > 0 and args[0]["name"] in ["self", "cls"]:
            is_method = True

        # Get function decorators
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Call) and isinstance(
                decorator.func, ast.Name
            ):
                decorators.append(f"{decorator.func.id}(...)")

        # Check for default arguments
        defaults = []
        if node.args.defaults:
            # Handle positional defaults
            positional_params = len(node.args.args) - len(node.args.defaults)
            for i, default in enumerate(node.args.defaults):
                param_idx = positional_params + i
                if param_idx < len(args):
                    default_str = ast.unparse(default)
                    defaults.append(
                        {"param": args[param_idx]["name"], "value": default_str}
                    )

        # Check for keyword-only defaults
        if node.args.kw_defaults:
            for i, default in enumerate(node.args.kw_defaults):
                if default and i < len(node.args.kwonlyargs):
                    kwarg = node.args.kwonlyargs[i]
                    default_str = ast.unparse(default)
                    defaults.append({"param": kwarg.arg, "value": default_str})

        return {
            "name": node.name,
            "line": node.lineno,
            "is_method": is_method,
            "args": args,
            "returns": returns,
            "docstring": docstring,
            "decorators": decorators,
            "defaults": defaults,
        }

    def _extract_class_info(self, node: ast.ClassDef, code: str) -> Dict[str, Any]:
        """Extract detailed information about a class."""
        # Get base classes
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(ast.unparse(base))

        # Get class docstring
        docstring = ast.get_docstring(node)

        # Get class methods
        methods = []
        class_variables = []

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._extract_function_info(item, code)
                methods.append(method_info)
            elif isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        value = None
                        if isinstance(item.value, (ast.Str, ast.Num, ast.NameConstant)):
                            value = ast.literal_eval(item.value)
                        elif isinstance(item.value, ast.Dict):
                            value = "{...}"  # Placeholder for dict
                        elif isinstance(item.value, ast.List):
                            value = "[...]"  # Placeholder for list

                        class_variables.append(
                            {"name": target.id, "value": value, "line": item.lineno}
                        )

        return {
            "name": node.name,
            "line": node.lineno,
            "bases": bases,
            "docstring": docstring,
            "methods": methods,
            "class_variables": class_variables,
        }

    def _generate_pytest_tests(
        self, analyzed_code: Dict[str, Any]
    ) -> str:  # noqa: C901
        """Generate pytest-style test cases."""
        test_code = []

        # Add necessary imports
        test_code.append("import pytest")

        # Add any imports from the original code
        for imp in analyzed_code.get("imports", []):
            if imp["type"] == "import":
                names = [n["asname"] or n["name"] for n in imp["names"]]
                test_code.append(f"import {', '.join(names)}")
            else:  # import_from
                names = [
                    f"{n['name']} as {n['asname']}" if n["asname"] else n["name"]
                    for n in imp["names"]
                ]
                test_code.append(f"from {imp['module']} import {', '.join(names)}")

        # Add blank line after imports
        test_code.append("")

        # Generate fixtures
        fixture_code = self._generate_pytest_fixtures(analyzed_code)
        if fixture_code:
            test_code.append(fixture_code)
            test_code.append("")

        # Generate function tests
        for func in analyzed_code.get("functions", []):
            # Skip if it's a private function (starts with _)
            if func["name"].startswith("_") and not func["name"].startswith("__"):
                continue

            test_code.append(f"def test_{func['name']}():")

            # Add docstring based on the original function
            if func["docstring"]:
                test_code.append(f'    """Test {func["name"]} function."""')
            else:
                test_code.append(f'    """Test {func["name"]} function."""')

            # Generate test implementation based on function signature
            args_setup = []
            for arg in func["args"]:
                if arg["name"] in ["self", "cls"]:
                    continue

                # Generate sample values based on parameter type
                if arg["annotation"]:
                    if "str" in arg["annotation"]:
                        args_setup.append(f'    {arg["name"]} = "test_{arg["name"]}"')
                    elif "int" in arg["annotation"]:
                        args_setup.append(f'    {arg["name"]} = 42')
                    elif "float" in arg["annotation"]:
                        args_setup.append(f'    {arg["name"]} = 3.14')
                    elif "bool" in arg["annotation"]:
                        args_setup.append(f'    {arg["name"]} = True')
                    elif "List" in arg["annotation"] or "list" in arg["annotation"]:
                        args_setup.append(f'    {arg["name"]} = []')
                    elif "Dict" in arg["annotation"] or "dict" in arg["annotation"]:
                        args_setup.append(f'    {arg["name"]} = {{}}')
                    else:
                        args_setup.append(
                            f'    {arg["name"]} = None  # TODO: Value for {arg["annotation"]}'
                        )
                else:
                    args_setup.append(
                        f'    {arg["name"]} = None  # TODO: Set appropriate value'
                    )

            # Add parameter setup
            if args_setup:
                test_code.extend(args_setup)
                test_code.append("")

            # Add function call
            arg_list = [
                a["name"] for a in func["args"] if a["name"] not in ["self", "cls"]
            ]
            if arg_list:
                test_code.append(f'    result = {func["name"]}({", ".join(arg_list)})')
            else:
                test_code.append(f'    result = {func["name"]}()')

            # Add assertions
            test_code.append("    # TODO: Add appropriate assertions")
            test_code.append("    assert result is not None")
            test_code.append("")

        # Generate class tests
        for cls in analyzed_code.get("classes", []):
            test_code.append(f"class Test{cls['name']}:")
            test_code.append(f'    """Test suite for {cls["name"]} class."""')
            test_code.append("")

            # Add setup method if the class has instance methods
            has_instance_methods = any(
                m["is_method"] and m["args"] and m["args"][0]["name"] == "self"
                for m in cls["methods"]
            )
            if has_instance_methods:
                test_code.append("    @pytest.fixture")
                test_code.append(f"    def {cls['name'].lower()}_instance(self):")
                test_code.append(
                    f'        """Create a {cls["name"]} instance for testing."""'
                )
                test_code.append(f"        return {cls['name']}()")
                test_code.append("")

            # Generate method tests
            for method in cls["methods"]:
                # Skip private methods
                if method["name"].startswith("_") and not method["name"].startswith(
                    "__"
                ):
                    continue

                # Skip __init__
                if method["name"] == "__init__":
                    continue

                # Determine function parameters and fixtures
                fixture_params = []
                if (
                    method["is_method"]
                    and method["args"]
                    and method["args"][0]["name"] == "self"
                ):
                    fixture_params.append(f"{cls['name'].lower()}_instance")

                # Determine function parameters
                if fixture_params:
                    test_code.append(
                        f"    def test_{method['name']}(self, {', '.join(fixture_params)}):"
                    )
                else:
                    test_code.append(f"    def test_{method['name']}(self):")

                # Add docstring
                test_code.append(f'        """Test {method["name"]} method."""')

                # Generate test implementation based on method signature
                args_setup = []

                # For static methods, include all args; for instance methods, skip self/cls
                args_to_process = (
                    method["args"][1:] if method["is_method"] else method["args"]
                )

                for arg in args_to_process:
                    # Generate sample values based on parameter type
                    if arg["annotation"]:
                        if "str" in arg["annotation"]:
                            args_setup.append(
                                f'        {arg["name"]} = "test_{arg["name"]}"'
                            )
                        elif "int" in arg["annotation"]:
                            args_setup.append(f'        {arg["name"]} = 42')
                        elif "float" in arg["annotation"]:
                            args_setup.append(f'        {arg["name"]} = 3.14')
                        elif "bool" in arg["annotation"]:
                            args_setup.append(f'        {arg["name"]} = True')
                        elif "List" in arg["annotation"] or "list" in arg["annotation"]:
                            args_setup.append(f'        {arg["name"]} = []')
                        elif (
                            "Dict" in arg["annotation"]
                            or "dict" in arg["annotation"]
                            or "dictionary" in arg["annotation"].lower()
                        ):
                            args_setup.append(f'        {arg["name"]} = {{}}')
                        else:
                            args_setup.append(
                                f'        {arg["name"]} = None  # TODO: Value for {arg["annotation"]}'
                            )
                    else:
                        args_setup.append(
                            f'        {arg["name"]} = None  # TODO: Set appropriate value'
                        )

                # Add parameter setup
                if args_setup:
                    test_code.extend(args_setup)
                    test_code.append("")

                # Add method call
                arg_list = []
                if (
                    method["is_method"]
                    and method["args"]
                    and method["args"][0]["name"] == "self"
                ):
                    arg_list = [a["name"] for a in method["args"][1:]]  # Skip self
                else:
                    arg_list = [
                        a["name"] for a in method["args"]
                    ]  # Include all args for static methods

                # Handle method call based on method type
                if (
                    method["is_method"]
                    and method["args"]
                    and method["args"][0]["name"] == "self"
                ):
                    if arg_list:
                        instance_name = f'{cls["name"].lower()}_instance'
                        test_code.append(
                            f'        result = {instance_name}.{method["name"]}({", ".join(arg_list)})'
                        )
                    else:
                        test_code.append(
                            f'        result = {cls["name"].lower()}_instance.{method["name"]}()'
                        )
                else:
                    # Static or class method
                    if arg_list:
                        test_code.append(
                            f'        result = {cls["name"]}.{method["name"]}({", ".join(arg_list)})'
                        )
                    else:
                        test_code.append(
                            f'        result = {cls["name"]}.{method["name"]}()'
                        )

                # Add assertions
                test_code.append("        # TODO: Add appropriate assertions")
                test_code.append("        assert result is not None")
                test_code.append("")

        return "\n".join(test_code)

    def _generate_pytest_fixtures(self, analyzed_code: Dict[str, Any]) -> str:
        """Generate pytest fixtures."""
        fixtures = []

        # Add conftest-style fixtures
        fixtures.append("@pytest.fixture")
        fixtures.append("def sample_data():")
        fixtures.append('    """Provide sample data for tests."""')
        fixtures.append("    return {")
        fixtures.append('        "id": 1,')
        fixtures.append('        "name": "test",')
        fixtures.append('        "value": 42')
        fixtures.append("    }")

        return "\n".join(fixtures)

    def _generate_unittest_tests(
        self, analyzed_code: Dict[str, Any]
    ) -> str:  # noqa: C901
        """Generate unittest-style test cases."""
        # Similar implementation to pytest but for unittest
        test_code = ["import unittest"]

        # Add imports from the original code
        for imp in analyzed_code.get("imports", []):
            if imp["type"] == "import":
                names = [n["asname"] or n["name"] for n in imp["names"]]
                test_code.append(f"import {', '.join(names)}")
            else:  # import_from
                names = [
                    f"{n['name']} as {n['asname']}" if n["asname"] else n["name"]
                    for n in imp["names"]
                ]
                test_code.append(f"from {imp['module']} import {', '.join(names)}")

        test_code.append("")

        # Generate function tests
        if analyzed_code.get("functions"):
            test_code.append("class TestFunctions(unittest.TestCase):")

            for func in analyzed_code.get("functions", []):
                if func["name"].startswith("_") and not func["name"].startswith("__"):
                    continue

                test_code.append(f"    def test_{func['name']}(self):")
                test_code.append(f'        """Test {func["name"]} function."""')

                # Similar test implementation as with pytest
                args_setup = []
                for arg in func["args"]:
                    if arg["name"] in ["self", "cls"]:
                        continue

                    if arg["annotation"]:
                        if "str" in arg["annotation"]:
                            args_setup.append(
                                f'        {arg["name"]} = "test_{arg["name"]}"'
                            )
                        elif "int" in arg["annotation"]:
                            args_setup.append(f'        {arg["name"]} = 42')
                        elif "float" in arg["annotation"]:
                            args_setup.append(f'        {arg["name"]} = 3.14')
                        elif "bool" in arg["annotation"]:
                            args_setup.append(f'        {arg["name"]} = True')
                        elif "List" in arg["annotation"] or "list" in arg["annotation"]:
                            args_setup.append(f'        {arg["name"]} = []')
                        elif "Dict" in arg["annotation"] or "dict" in arg["annotation"]:
                            args_setup.append(f'        {arg["name"]} = {{}}')
                        else:
                            args_setup.append(
                                f'        {arg["name"]} = None  # TODO: Value for {arg["annotation"]}'
                            )
                    else:
                        args_setup.append(
                            f'        {arg["name"]} = None  # TODO: Set appropriate value'
                        )

                if args_setup:
                    test_code.extend(args_setup)
                    test_code.append("")

                arg_list = [
                    a["name"] for a in func["args"] if a["name"] not in ["self", "cls"]
                ]
                if arg_list:
                    test_code.append(
                        f'        result = {func["name"]}({", ".join(arg_list)})'
                    )
                else:
                    test_code.append(f'        result = {func["name"]}()')

                test_code.append("        # TODO: Add appropriate assertions")
                test_code.append("        self.assertIsNotNone(result)")
                test_code.append("")

        # Generate class tests
        for cls in analyzed_code.get("classes", []):
            test_code.append(f"class Test{cls['name']}(unittest.TestCase):")
            test_code.append(f'    """Test suite for {cls["name"]} class."""')
            test_code.append("")

            # Add setup method
            test_code.append("    def setUp(self):")
            test_code.append('        """Set up test fixtures."""')
            test_code.append(f"        self.instance = {cls['name']}()")
            test_code.append("")

            # Generate method tests
            for method in cls["methods"]:
                if method["name"].startswith("_") and not method["name"].startswith(
                    "__"
                ):
                    continue

                if method["name"] == "__init__":
                    continue

                test_code.append(f"    def test_{method['name']}(self):")
                test_code.append(f'        """Test {method["name"]} method."""')

                args_setup = []
                # For static methods, include all args; for instance methods, skip self
                args_to_process = (
                    method["args"][1:]
                    if method["is_method"] and method["args"][0]["name"] == "self"
                    else method["args"]
                )

                for arg in args_to_process:
                    if arg["annotation"]:
                        if "str" in arg["annotation"]:
                            args_setup.append(
                                f'        {arg["name"]} = "test_{arg["name"]}"'
                            )
                        elif "int" in arg["annotation"]:
                            args_setup.append(f'        {arg["name"]} = 42')
                        elif "float" in arg["annotation"]:
                            args_setup.append(f'        {arg["name"]} = 3.14')
                        elif "bool" in arg["annotation"]:
                            args_setup.append(f'        {arg["name"]} = True')
                        elif "List" in arg["annotation"] or "list" in arg["annotation"]:
                            args_setup.append(f'        {arg["name"]} = []')
                        elif (
                            "Dict" in arg["annotation"]
                            or "dict" in arg["annotation"]
                            or "dictionary" in arg["annotation"].lower()
                        ):
                            args_setup.append(f'        {arg["name"]} = {{}}')
                        else:
                            args_setup.append(
                                f'        {arg["name"]} = None  # TODO: Value for {arg["annotation"]}'
                            )
                    else:
                        args_setup.append(
                            f'        {arg["name"]} = None  # TODO: Set appropriate value'
                        )

                if args_setup:
                    test_code.extend(args_setup)
                    test_code.append("")

                # Determine argument list based on method type
                arg_list = []
                if (
                    method["is_method"]
                    and method["args"]
                    and method["args"][0]["name"] == "self"
                ):
                    arg_list = [a["name"] for a in method["args"][1:]]  # Skip self
                else:
                    arg_list = [
                        a["name"] for a in method["args"]
                    ]  # Include all args for static methods

                # Generate method call based on method type (instance vs. static/class)
                if (
                    method["is_method"]
                    and method["args"]
                    and method["args"][0]["name"] == "self"
                ):
                    if arg_list:
                        test_code.append(
                            f'        result = self.instance.{method["name"]}({", ".join(arg_list)})'
                        )
                    else:
                        test_code.append(
                            f'        result = self.instance.{method["name"]}()'
                        )
                else:
                    # For static or class methods
                    if arg_list:
                        test_code.append(
                            f'        result = {cls["name"]}.{method["name"]}({", ".join(arg_list)})'
                        )
                    else:
                        test_code.append(
                            f'        result = {cls["name"]}.{method["name"]}()'
                        )

                test_code.append("        # TODO: Add appropriate assertions")
                test_code.append("        self.assertIsNotNone(result)")
                test_code.append("")

        test_code.append("if __name__ == '__main__':")
        test_code.append("    unittest.main()")

        return "\n".join(test_code)
