from unittest.mock import MagicMock, patch

from packages.agents.advanced_reasoning.agents import (
    DependencyAgent,
    TestGeneratorAgent,
)


def test_test_generator_agent():
    with patch("ollama.Client") as mock_client:
        mock_instance = MagicMock()
        mock_instance.chat.return_value.message.content = (
            "def test_example(): assert True"
        )
        mock_client.return_value = mock_instance

        agent = TestGeneratorAgent()
        result = agent.generate_tests("module.py")

        assert "def test_example()" in result
        mock_instance.chat.assert_called_once()


def test_dependency_agent():
    with (
        patch("os.walk") as mock_walk,
        patch("builtins.open", create=True),
        patch("ast.parse"),
    ):
        mock_walk.return_value = [("/root", [], ["test.py"])]

        # Mock file opening and reading
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = "import os\nimport sys"

        # Mock AST parsing to return known imports
        MagicMock()
        mock_import = MagicMock()
        mock_import.module = None
        mock_alias1 = MagicMock()
        mock_alias1.name = "os"
        mock_alias2 = MagicMock()
        mock_alias2.name = "sys"
        mock_import.names = [mock_alias1, mock_alias2]

        with patch("ast.walk", return_value=[mock_import]):
            agent = DependencyAgent()
            result = agent.analyze_deps("/root")

            assert "test.py" in result
            assert sorted(result["test.py"]) == ["os", "sys"]
