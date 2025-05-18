from typing import Any, Dict, List  # Removed unused Optional

from ..core.base import Agent
from ..core.registry import register_agent


@register_agent("dependency")
class DependencyAgent(Agent):
    """
    Agent responsible for analyzing and managing dependencies in code.
    """

    def __init__(
        self, analyze_unused: bool = True, suggest_versions: bool = True, **kwargs
    ):
        super().__init__(**kwargs)
        self.analyze_unused = analyze_unused
        self.suggest_versions = suggest_versions

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        self.add_to_history("input", input_data)
        code = input_data.get("code", "")
        if not isinstance(code, str):
            raise ValueError("Input 'code' must be a string.")
        result = {
            "dependencies": self._extract_dependencies(code),
            "missing": [],
            "unused": [] if self.analyze_unused else None,
            "recommendations": {} if self.suggest_versions else None,
        }
        self.add_to_history("output", result)
        return result

    def _extract_dependencies(self, code: str) -> List[Dict[str, str]]:
        # Dummy implementation for demonstration
        # Replace with real AST parsing logic
        lines = code.splitlines()
        deps = []
        for line in lines:
            if line.startswith("import "):
                for name in line.replace("import ", "").split(","):
                    deps.append({"name": name.strip(), "import_type": "import"})
            elif line.startswith("from "):
                parts = line.split()
                if len(parts) > 1:
                    deps.append({"name": parts[1], "import_type": "from"})
        return deps
