import os
import tempfile

import pytest

from packages.agents import DependencyAgent


def test_analyze_deps_empty_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        agent = DependencyAgent()
        result = agent.analyze_deps(tmpdir)
        assert result == {}


def test_analyze_deps_with_imports():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.py")
        with open(test_file, "w") as f:
            f.write("import os\nimport sys\nfrom pathlib import Path")
        agent = DependencyAgent()
        result = agent.analyze_deps(tmpdir)
        assert "test.py" in result
        assert set(result["test.py"]) == {"os", "sys", "pathlib"}
