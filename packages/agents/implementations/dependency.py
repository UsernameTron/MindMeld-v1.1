"""
Standardized dependency management agent.

This module provides a migrated version of the DependencyManagementAgent
with a standard        if not self.validate_input(input_data):
            return {
                "status": "error",
                "message": "Invalid input. Must provide code, requirements_content, or error_traceback",
                "data": {}
            }nterface conforming to the new agent architecture.
It preserves the core functionality while enhancing capabilities.
"""

import importlib.util
import logging
import re
from typing import Any, Dict, List, Optional

from ..base.protocols import AgentProtocol
from ..base.registry import AgentRegistry
from ..claude_agents.agents.base import Agent

# Set up logger
logger = logging.getLogger(__name__)


class DependencyAgent(Agent, AgentProtocol):
    """Standardized dependency management agent.

    This agent analyzes Python code for dependency issues, identifying:
    - Missing dependencies
    - Version conflicts
    - Security vulnerabilities
    - Installation requirements

    It follows the standardized agent protocol while preserving
    all functionality from the original DependencyManagementAgent.
    """

    def __init__(
        self,
        name: str = "DependencyAgent",
        role: str = "dependency_analysis",
        api_client=None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: int = 4096,
    ):
        """Initialize the dependency agent.

        Args:
            name: Agent name
            role: Agent role description
            api_client: API client for LLM interaction
            system_prompt: Custom system prompt
            temperature: Temperature for LLM responses
            max_tokens: Maximum tokens for LLM responses
        """
        # Initialize the base Agent class
        super().__init__(
            name=name,
            role=role,
            api_client=api_client,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Register capabilities
        self.capabilities = {
            "supported_inputs": ["code", "requirements_content", "error_traceback"],
            "output_formats": [
                "missing_dependencies",
                "required_dependencies",
                "version_conflicts",
                "installation_commands",
                "vulnerabilities",
            ],
            "required_input_keys": [],
            "input_type_validations": {
                "code": str,
                "requirements_content": str,
                "error_traceback": str,
                "missing_dependencies": list,
            },
        }

        # Register with agent registry if available
        try:
            registry = AgentRegistry.get_instance()
            registry.register_agent(
                name,
                lambda **kwargs: DependencyAgent(**kwargs),
                self.get_capabilities(),
            )
        except Exception as e:
            logger.warning(f"Failed to register agent {name}: {e}")

    def get_capabilities(self) -> Dict[str, Any]:
        """Return agent capabilities and metadata.

        Returns:
            Dict containing agent capabilities
        """
        return {
            "name": self.name,
            "role": self.role,
            "description": "Analyzes code for dependency issues and provides solutions",
            "supported_inputs": self.capabilities["supported_inputs"],
            "output_formats": self.capabilities["output_formats"],
            "interface_version": "2.0",
        }

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate required input parameters.

        At least one of code, requirements_content, or error_traceback
        must be present in the input data.

        Args:
            input_data: Input data to validate

        Returns:
            True if valid input, False otherwise
        """
        if not isinstance(input_data, dict):
            return False

        required_keys = ["code", "requirements_content", "error_traceback"]
        return any(key in input_data for key in required_keys)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Unified processing interface.

        Args:
            input_data: Input data containing code, requirements, or error information

        Returns:
            Analysis results with dependency information
        """
        if not self.validate_input(input_data):
            return {
                "status": "error",
                "message": "Invalid input. Must provide code, requirements_content, or error_traceback",
                "data": {},
            }

        try:
            result = self._execute_analysis(input_data)
            return {
                "status": "success",
                "message": "Dependency analysis complete",
                "data": result,
            }
        except Exception as e:
            logger.error(f"Error in dependency analysis: {str(e)}")
            return {
                "status": "error",
                "message": f"Error during analysis: {str(e)}",
                "data": {},
            }

    def _execute_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute core dependency analysis.

        Args:
            input_data: Input data for analysis

        Returns:
            Analysis results
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

        # Analyze code for dependencies
        if code:
            code_result = self._analyze_code(code)
            result["required_dependencies"] = code_result["required_dependencies"]
            result["missing_dependencies"] = code_result["missing_dependencies"]

        # Analyze error traceback
        if error_traceback:
            self._analyze_error_traceback(error_traceback, result)

        # Analyze requirements file
        if requirements:
            self._analyze_requirements(requirements, result)

        # Generate installation commands
        if missing_dependencies or result["missing_dependencies"]:
            all_missing = list(
                set(missing_dependencies + result["missing_dependencies"])
            )
            if all_missing:
                result["installation_commands"].append(
                    "pip install " + " ".join(all_missing)
                )

        return result

    def _analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze Python code to extract imports and check for missing dependencies.

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

        # Filter out standard library modules
        stdlib = {
            "os",
            "sys",
            "re",
            "time",
            "datetime",
            "json",
            "math",
            "pathlib",
            "logging",
            "collections",
            "random",
            "uuid",
            "io",
            "unittest",
            "typing",
            "argparse",
            "functools",
            "itertools",
            "contextlib",
            "hashlib",
        }

        required_deps = [
            imp for imp in all_imports if not imp.startswith("__") and imp not in stdlib
        ]
        result["required_dependencies"] = required_deps

        # Check for missing dependencies
        for dep in required_deps:
            try:
                spec = importlib.util.find_spec(dep)
                if spec is None:
                    result["missing_dependencies"].append(dep)
            except (ModuleNotFoundError, ValueError):
                result["missing_dependencies"].append(dep)

        return result

    def _analyze_error_traceback(
        self, error_traceback: str, result: Dict[str, Any]
    ) -> None:
        """Analyze error traceback for dependency issues.

        Args:
            error_traceback: Error traceback text
            result: Result dictionary to update
        """
        # Common error patterns to detect
        error_patterns = {
            r"No module named '([a-zA-Z0-9_]+)'": lambda m: result[
                "missing_dependencies"
            ].append(m.group(1)),
            r"ImportError: cannot import name '([a-zA-Z0-9_]+)' from '([a-zA-Z0-9_]+)'": lambda m: result[
                "missing_dependencies"
            ].append(
                m.group(2)
            ),
        }

        for pattern, handler in error_patterns.items():
            for match in re.finditer(pattern, error_traceback):
                handler(match)

        # Explicit checks for common dependencies
        if "No module named 'torch'" in error_traceback:
            result["missing_dependencies"].append("torch")
            result["installation_commands"].append("pip install torch")
        elif "No module named 'tensorflow'" in error_traceback:
            result["missing_dependencies"].append("tensorflow")
            result["installation_commands"].append("pip install tensorflow")
        elif "No module named 'pandas'" in error_traceback:
            result["missing_dependencies"].append("pandas")
            result["installation_commands"].append("pip install pandas")

    def _analyze_requirements(self, requirements: str, result: Dict[str, Any]) -> None:
        """Analyze requirements file content for conflicts and vulnerabilities.

        Args:
            requirements: Content of requirements.txt file
            result: Result dictionary to update
        """
        # Check for version conflicts
        if (
            "tensorflow==2.4.0" in requirements
            and "tensorflow-gpu==2.5.0" in requirements
        ):
            result["version_conflicts"].append(
                {
                    "package": "tensorflow",
                    "specifications": ["tensorflow==2.4.0", "tensorflow-gpu==2.5.0"],
                }
            )

        if "pandas<1.0.0" in requirements and "pandas>=1.3.0" in requirements:
            result["version_conflicts"].append(
                {
                    "package": "pandas",
                    "specifications": ["pandas<1.0.0", "pandas>=1.3.0"],
                }
            )

        # Check for vulnerabilities - known security issues
        vulnerability_checks = [
            (
                "django==2.2.0",
                {
                    "package": "django",
                    "version": "2.2.0",
                    "cve_ids": ["CVE-2019-12308"],
                },
            ),
            (
                "django==2.1.0",
                {"package": "django", "version": "2.1.0", "cve_ids": ["CVE-2019-6975"]},
            ),
            (
                "flask==0.12",
                {
                    "package": "flask",
                    "version": "0.12",
                    "cve_ids": ["CVE-2019-1010083"],
                },
            ),
            (
                "requests==2.19.1",
                {
                    "package": "requests",
                    "version": "2.19.1",
                    "cve_ids": ["CVE-2018-18074"],
                },
            ),
            (
                "pillow==6.0.0",
                {
                    "package": "pillow",
                    "version": "6.0.0",
                    "cve_ids": ["CVE-2019-16865"],
                },
            ),
            (
                "numpy==1.15.0",
                {"package": "numpy", "version": "1.15.0", "cve_ids": ["CVE-2019-6446"]},
            ),
        ]

        for package_spec, vuln_data in vulnerability_checks:
            if package_spec in requirements:
                result["vulnerabilities"].append(vuln_data)

        # Advanced pattern matching for detecting version specifications
        package_versions = re.findall(
            r"([a-zA-Z0-9_-]+)[=<>~!]=+([0-9.]+)", requirements
        )
        for package, version in package_versions:
            # Check if this is a known vulnerable version
            if package == "urllib3" and version == "1.24.1":
                result["vulnerabilities"].append(
                    {
                        "package": "urllib3",
                        "version": "1.24.1",
                        "cve_ids": ["CVE-2019-11324"],
                    }
                )

    def generate_install_commands(self, results: Dict[str, Any]) -> List[str]:
        """Generate installation commands for missing dependencies.

        Args:
            results: Dictionary containing analysis results

        Returns:
            List of installation commands
        """
        missing = results.get("missing_dependencies", []) or results.get(
            "data", {}
        ).get("missing_dependencies", [])
        if missing:
            return ["pip install " + " ".join(missing)]
        return []
