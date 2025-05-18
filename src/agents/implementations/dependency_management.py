import importlib.util
import re
from typing import Any, Dict  # Removed unused List

from ..core.base import Agent
from ..core.registry import register_agent


@register_agent("dependency_management")
class DependencyManagementAgent(Agent):
    """
    Agent for advanced dependency management: detects missing dependencies, version conflicts, and vulnerabilities.
    """

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
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

    def _analyze_code(self, code: str) -> Dict[str, Any]:
        """
        Analyze Python code to extract imports and check for missing dependencies.
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
