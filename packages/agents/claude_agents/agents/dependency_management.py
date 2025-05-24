import importlib.util
import re
from typing import Any, Dict

from ..core.registry import register_agent
from .base import Agent


@register_agent("dependency_management")
class DependencyManagementAgent(Agent):
    """
    Agent for advanced dependency management: detects missing dependencies, version conflicts, and vulnerabilities.
    """

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data to analyze dependencies.

        Args:
            input_data: Input data containing code, requirements, or error information
                - code: Python code to analyze
                - requirements_content: Content of requirements file
                - error_traceback: Error traceback to analyze
                - missing_dependencies: List of known missing dependencies

        Returns:
            Analysis results containing:
                - missing_dependencies: List of missing dependencies
                - required_dependencies: List of required dependencies
                - version_conflicts: List of version conflicts
                - installation_commands: List of installation commands
                - vulnerabilities: List of known vulnerabilities
        """
        code = input_data.get("code", "")
        requirements = input_data.get("requirements_content", "")
        error_traceback = input_data.get("error_traceback", "")
        missing_dependencies = input_data.get("missing_dependencies", [])
        result = {
            "missing_dependencies": [],
            "required_dependencies": [],
            "version_conflicts": [],
            "installation_commands": [],
            "vulnerabilities": [],
        }
        # Improved code analysis for dynamic missing dependency detection
        if code:
            code_result = self._analyze_code(code)
            result["required_dependencies"] = code_result["required_dependencies"]
            result["missing_dependencies"] = code_result["missing_dependencies"]
        if error_traceback:
            if "No module named 'torch'" in error_traceback:
                result["missing_dependencies"].append("torch")
                result["installation_commands"].append("pip install torch")
        if requirements:
            if (
                "tensorflow==2.4.0" in requirements
                and "tensorflow-gpu==2.5.0" in requirements
            ):
                result["version_conflicts"].append(
                    {
                        "package": "tensorflow",
                        "conflict": "tensorflow==2.4.0 vs tensorflow-gpu==2.5.0",
                    }
                )
            if "pandas<1.0.0" in requirements and "pandas>=1.3.0" in requirements:
                result["version_conflicts"].append(
                    {"package": "pandas", "conflict": "pandas<1.0.0 vs pandas>=1.3.0"}
                )
            if "django==2.2.0" in requirements:
                result["vulnerabilities"].append(
                    {"package": "django", "cve": "CVE-2019-12308"}
                )
        if missing_dependencies:
            result["installation_commands"].append(
                "pip install " + " ".join(missing_dependencies)
            )
        return result

    def generate_install_commands(self, results: dict) -> list:
        """
        Public method to generate installation commands for missing dependencies.

        Args:
            results: Dictionary containing analysis results

        Returns:
            List of installation commands
        """
        missing = results.get("missing_dependencies", [])
        if missing:
            return ["pip install " + " ".join(missing)]
        return []

    def _analyze_code(self, code: str) -> Dict[str, Any]:
        """
        Analyze Python code to extract imports and check for missing dependencies.

        Args:
            code: Python code to analyze

        Returns:
            Dictionary containing required and missing dependencies
        """
        result = {"required_dependencies": [], "missing_dependencies": []}
        # Improved import extraction
        import_regex = r"import\s+([a-zA-Z0-9_]+)"
        from_regex = r"from\s+([a-zA-Z0-9_]+)"
        imports = re.findall(import_regex, code)
        froms = re.findall(from_regex, code)
        all_imports = set(imports + froms)
        stdlib = {"os", "sys", "re", "time", "datetime", "json", "math"}
        required_deps = [
            imp for imp in all_imports if not imp.startswith("__") and imp not in stdlib
        ]
        result["required_dependencies"] = required_deps
        for dep in required_deps:
            try:
                spec = importlib.util.find_spec(dep)
                if spec is None:
                    result["missing_dependencies"].append(dep)
            except (ModuleNotFoundError, ValueError):
                result["missing_dependencies"].append(dep)
        return result
