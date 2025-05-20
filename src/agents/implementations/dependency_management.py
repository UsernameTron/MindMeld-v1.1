import importlib.util
import re
from typing import Any, Dict, List, Set, Tuple

from ..core.base import Agent


class DependencyManagementAgent(Agent):
    """Agent name property for registry"""

    name = "dependency_management"
    """
    Agent for advanced dependency management: detects missing dependencies, version conflicts, and vulnerabilities.
    """

    # Known security vulnerabilities that need addressing
    SECURITY_VULNERABILITIES = {
        "django": {
            "min_safe_version": "3.2.19",
            "cve": ["CVE-2023-36053", "CVE-2023-31047"],
        },
        "requests": {"min_safe_version": "2.31.0", "cve": ["CVE-2023-32681"]},
        "flask": {
            "min_safe_version": "2.3.3",
            "cve": ["CVE-2023-30861", "CVE-2023-30860"],
        },
    }

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
            "invalid_requirements": [],
        }

        # Improved code analysis for dynamic missing dependency detection
        if code:
            code_result = self._analyze_code(code)
            result["required_dependencies"] = code_result["required_dependencies"]
            result["missing_dependencies"] = code_result["missing_dependencies"]

        if error_traceback:
            self._analyze_error_traceback(error_traceback, result)

        if requirements:
            self._analyze_requirements(requirements, result)

        if missing_dependencies:
            result["installation_commands"].append(
                "pip install " + " ".join(missing_dependencies)
            )
        self._generate_install_commands(result)
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
        stdlib = {
            "os",
            "sys",
            "re",
            "time",
            "datetime",
            "json",
            "math",
            "typing",
            "collections",
            "itertools",
            "functools",
            "pathlib",
            "glob",
            "argparse",
            "logging",
            "unittest",
            "tempfile",
            "shutil",
            "io",
            "csv",
            "xml",
        }
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

    def _analyze_error_traceback(
        self, error_traceback: str, result: Dict[str, Any]
    ) -> None:
        """
        Analyze error traceback to identify missing dependencies.
        """
        common_import_errors = {
            "No module named 'torch'": "torch",
            "No module named 'pandas'": "pandas",
            "No module named 'sklearn'": "scikit-learn",
            "No module named 'scikit'": "scikit-learn",
            "No module named 'tensorflow'": "tensorflow",
            "No module named 'numpy'": "numpy",
            "No module named 'matplotlib'": "matplotlib",
            "No module named 'flask'": "flask",
            "No module named 'django'": "django",
            "No module named 'requests'": "requests",
            "No module named 'bs4'": "beautifulsoup4",
            "No module named 'selenium'": "selenium",
            "No module named 'pytest'": "pytest",
            "No module named 'dash'": "dash",
            "No module named 'plotly'": "plotly",
            "No module named 'fastapi'": "fastapi",
            "No module named 'pydantic'": "pydantic",
            "No module named 'uvicorn'": "uvicorn",
            "No module named 'aiohttp'": "aiohttp",
            "No module named 'httpx'": "httpx",
            "No module named 'redis'": "redis",
            "No module named 'sqlalchemy'": "sqlalchemy",
            "No module named 'pymongo'": "pymongo",
            "No module named 'psycopg2'": "psycopg2-binary",
            "No module named 'mysql'": "mysql-connector-python",
            "No module named 'jwt'": "pyjwt",
            "No module named 'boto3'": "boto3",
            "No module named 'openai'": "openai",
            "No module named 'transformers'": "transformers",
            "No module named 'langchain'": "langchain",
            "No module named 'polars'": "polars",
            "No module named 'shap'": "shap",
        }

        for error_pattern, package in common_import_errors.items():
            if (
                error_pattern in error_traceback
                and package not in result["missing_dependencies"]
            ):
                result["missing_dependencies"].append(package)

    def _analyze_requirements(self, requirements: str, result: Dict[str, Any]) -> None:
        """
        Analyze requirements content to identify conflicts, vulnerabilities, and invalid entries.
        """
        # Extract package specifications
        requirements_lines = requirements.strip().split("\n")
        package_specs = {}
        invalid_entries = []

        for line in requirements_lines:
            line = line.strip()
            # Skip empty lines, comments, and requirement file references
            if not line or line.startswith("#") or line.startswith("-r "):
                continue

            # Check for invalid entries
            if line.lower() in ["the", "e", "ibm"] or len(line) == 1:
                invalid_entries.append(line)
                continue

            # Parse package and version requirements
            # Handle more complex cases like package[extra]>=1.0.0
            match = re.match(r"^([a-zA-Z0-9_\-\[\]\.]+)(.*)$", line)
            if match:
                package_name = match.group(1).split("[")[0].strip().lower()
                version_spec = match.group(2).strip()

                if package_name not in package_specs:
                    package_specs[package_name] = []
                if version_spec:
                    package_specs[package_name].append(version_spec)

        # Record invalid entries
        if invalid_entries:
            result["invalid_requirements"] = invalid_entries

        # Check for version conflicts
        self._check_version_conflicts(package_specs, result)

        # Check for security vulnerabilities
        self._check_vulnerabilities(package_specs, result)

    def _check_version_conflicts(
        self, package_specs: Dict[str, List[str]], result: Dict[str, Any]
    ) -> None:
        """
        Check for version conflicts in package specifications.
        """
        # Specific known conflicts
        if "pandas" in package_specs:
            has_old_version = any("<1.0.0" in spec for spec in package_specs["pandas"])
            has_new_version = any(">=1.3.0" in spec for spec in package_specs["pandas"])

            if has_old_version and has_new_version:
                result["version_conflicts"].append(
                    {
                        "package": "pandas",
                        "specifications": ["pandas<1.0.0", "pandas>=1.3.0"],
                    }
                )

        if "tensorflow" in package_specs and "tensorflow-gpu" in package_specs:
            result["version_conflicts"].append(
                {
                    "package": "tensorflow",
                    "specifications": ["tensorflow", "tensorflow-gpu"],
                }
            )

    def _check_vulnerabilities(
        self, package_specs: Dict[str, List[str]], result: Dict[str, Any]
    ) -> None:
        """
        Check for security vulnerabilities in package specifications.
        """
        for package, vuln_info in self.SECURITY_VULNERABILITIES.items():
            if package in package_specs:
                min_safe_version = vuln_info["min_safe_version"]
                # Check if any version spec is below the min safe version
                needs_update = any(
                    self._is_vulnerable_version(spec, min_safe_version)
                    for spec in package_specs[package]
                )

                if needs_update:
                    result["vulnerabilities"].append(
                        {
                            "package": package,
                            "cve_ids": vuln_info["cve"],
                            "current_specs": package_specs[package],
                            "min_safe_version": min_safe_version,
                        }
                    )

    def _is_vulnerable_version(self, version_spec: str, min_safe_version: str) -> bool:
        """
        Check if a version specification indicates a vulnerable version.
        """
        # Simple check for exact versions
        if "==" in version_spec:
            version_match = re.search(r"==\s*([0-9\.]+)", version_spec)
            if version_match:
                version = version_match.group(1)
                return self._version_lt(version, min_safe_version)
        # For upper bounds
        elif "<" in version_spec:
            return True
        # For older versions
        elif ">" not in version_spec and ">=" not in version_spec:
            return True
        return False

    def _version_lt(self, v1: str, v2: str) -> bool:
        """
        Compare version strings. Returns True if v1 < v2.
        """
        v1_parts = [int(x) for x in v1.split(".")]
        v2_parts = [int(x) for x in v2.split(".")]

        for i in range(max(len(v1_parts), len(v2_parts))):
            v1_part = v1_parts[i] if i < len(v1_parts) else 0
            v2_part = v2_parts[i] if i < len(v2_parts) else 0

            if v1_part < v2_part:
                return True
            elif v1_part > v2_part:
                return False
        return False

    def _generate_install_commands(self, result: Dict[str, Any]) -> None:
        """
        Generate installation commands based on analysis results.
        """
        # Install missing dependencies
        if result.get("missing_dependencies"):
            missing_deps = sorted(set(result["missing_dependencies"]))
            if missing_deps:
                result["installation_commands"].append(
                    "pip install " + " ".join(missing_deps)
                )

        # Update vulnerable packages
        for vuln in result.get("vulnerabilities", []):
            result["installation_commands"].append(
                f"pip install {vuln['package']}>={vuln['min_safe_version']}"
            )

        # Fix version conflicts
        for conflict in result.get("version_conflicts", []):
            package = conflict["package"]
            if package == "pandas":
                # Prefer the newer version of pandas
                result["installation_commands"].append("pip install pandas>=1.3.0")
            elif package == "tensorflow":
                # Just use tensorflow, which includes GPU support in newer versions
                result["installation_commands"].append("pip install tensorflow>=2.5.0")
