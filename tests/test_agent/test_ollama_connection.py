"""
Unit tests for Ollama connection error handling.
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import requests

# Add parent directory to system path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the script modules to test
import run_agent
import scripts.wait_for_ollama as wait_for_ollama
from packages.agents.advanced_reasoning.agents import Agent


class TestOllamaConnection:
    """Tests for Ollama connection handling."""

    @patch("requests.get")
    def test_ollama_connection_success(self, mock_get):
        """Test successful Ollama connection check."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Act - create an agent to trigger the connection check
        agent = Agent(name="test_agent", model="test_model")

        # Call the wait_for_ollama directly to test its functionality
        with patch("builtins.print") as mock_print:
            result = wait_for_ollama.check_ollama_ready("http://localhost:11434")

        # Assert
        assert result is True
        mock_get.assert_called_with("http://localhost:11434/api/tags", timeout=5)

    @patch("requests.get")
    def test_ollama_connection_failure(self, mock_get):
        """Test Ollama connection failure handling."""
        # Arrange
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        # Act
        with patch("builtins.print") as mock_print:
            result = wait_for_ollama.check_ollama_ready("http://localhost:11434")

        # Assert
        assert result is False
        mock_get.assert_called_with("http://localhost:11434/api/tags", timeout=5)

    @patch("requests.get")
    def test_ollama_bad_status_code(self, mock_get):
        """Test handling of non-200 status codes from Ollama."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        # Act
        with patch("builtins.print") as mock_print:
            result = wait_for_ollama.check_ollama_ready("http://localhost:11434")

        # Assert
        assert result is False
        mock_get.assert_called_with("http://localhost:11434/api/tags", timeout=5)

    @patch("requests.get")
    @patch("time.sleep", return_value=None)
    def test_wait_for_ollama_timeout(self, mock_sleep, mock_get):
        """Test wait_for_ollama timeout logic."""
        # Arrange
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        # Act
        with (
            patch("logging.Logger.info") as mock_log,
            patch("logging.Logger.error") as mock_error,
            patch("sys.exit") as mock_exit,
        ):

            # Use main function with custom args to test timeout
            args = wait_for_ollama.parse_args(
                [
                    "--host",
                    "http://localhost:11434",
                    "--timeout",
                    "10",
                    "--interval",
                    "2",
                ]
            )
            wait_for_ollama.main(args)

        # Assert
        # Should call get multiple times (timeout/interval)
        assert mock_get.call_count >= 3
        assert mock_sleep.call_count >= 3
        mock_exit.assert_called_once_with(1)

    @patch("requests.get")
    @patch("wait_for_ollama.check_model_exists")
    def test_model_checking(self, mock_check_model, mock_get):
        """Test model checking functionality."""
        # Arrange
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        mock_check_model.return_value = False  # Model doesn't exist

        # Act
        with (
            patch("wait_for_ollama.pull_model") as mock_pull,
            patch("logging.Logger.info") as mock_log,
        ):
            result = wait_for_ollama.ensure_model_available(
                "http://localhost:11434", "llama2"
            )

        # Assert
        mock_check_model.assert_called_once_with("http://localhost:11434", "llama2")
        mock_pull.assert_called_once_with("http://localhost:11434", "llama2")


class TestAgentOllamaErrorHandling:
    """Tests for Agent error handling specific to Ollama connection issues."""

    @patch("packages.agents.advanced_reasoning.agents.Client")
    def test_connection_error_handling(self, mock_client):
        """Test agent handling of connection errors."""
        # Arrange
        mock_client_instance = MagicMock()
        mock_client_instance.chat.side_effect = ConnectionError(
            "Failed to connect to Ollama"
        )
        mock_client.return_value = mock_client_instance

        agent = Agent(name="test_agent", model="test_model")

        # Act
        with patch("builtins.print") as mock_print:
            result = agent.run("Test prompt", retries=2)

        # Assert
        assert isinstance(result, dict)
        assert "error" in result
        assert "Check if Ollama is running" in result["details"]
