"""
Unit tests for Agent retry and fallback mechanisms.
"""
import os
import pytest
import time
from unittest.mock import patch, MagicMock
import json
import sys
from pathlib import Path

# Add parent directory to system path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from packages.agents.advanced_reasoning.agents import Agent

class TestAgentRetry:
    """Tests for the Agent class retry and fallback mechanisms."""
    
    def setup_method(self):
        """Setup test environment before each test."""
        # Save original environment variables to restore later
        self.original_env = os.environ.copy()
        
        # Set test environment variables
        os.environ["MAX_RETRIES"] = "3"
        os.environ["BASE_TIMEOUT"] = "10"
        os.environ["FALLBACK_MODEL"] = "llama2"
        
        # Create agent instance for testing
        self.agent = Agent(name="test_agent", model="test_model")
    
    def teardown_method(self):
        """Clean up after each test."""
        # Restore original environment variables
        os.environ.clear()
        os.environ.update(self.original_env)
    
    @patch('packages.agents.advanced_reasoning.agents.Client')
    def test_agent_initialization(self, mock_client):
        """Test that agent initializes with correct parameters."""
        # Arrange
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        # Act
        agent = Agent(name="test_agent", model="test_model")
        
        # Assert
        assert agent.name == "test_agent"
        assert agent.model == "test_model"
        assert agent.max_retries == 3
        assert agent.base_timeout == 10
        assert agent.fallback_model == "llama2"
    
    @patch('packages.agents.advanced_reasoning.agents.Client')
    def test_agent_successful_run(self, mock_client):
        """Test agent run with successful API call."""
        # Arrange
        mock_client_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.message = {"content": "Test response"}
        mock_client_instance.chat.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        # Act
        result = self.agent.run("Test prompt")
        
        # Assert
        assert result == "Test response"
        mock_client_instance.chat.assert_called_once_with(
            model="test_model", 
            messages=[{"role": "user", "content": "[test_agent] Test prompt"}]
        )
    
    @patch('packages.agents.advanced_reasoning.agents.Client')
    @patch('packages.agents.advanced_reasoning.agents.time')
    def test_agent_retry_success(self, mock_time, mock_client):
        """Test that agent properly retries after failures."""
        # Arrange
        mock_client_instance = MagicMock()
        
        # First call fails, second succeeds
        mock_client_instance.chat.side_effect = [
            Exception("Connection error"),
            MagicMock(message={"content": "Success after retry"})
        ]
        
        mock_client.return_value = mock_client_instance
        
        # Act
        result = self.agent.run("Test prompt")
        
        # Assert
        assert result == "Success after retry"
        assert mock_client_instance.chat.call_count == 2
        assert mock_time.sleep.call_count == 1
    
    @patch('packages.agents.advanced_reasoning.agents.Client')
    @patch('packages.agents.advanced_reasoning.agents.time')
    def test_agent_fallback_model(self, mock_time, mock_client):
        """Test that agent uses fallback model when all retries fail."""
        # Arrange
        mock_client_instance = MagicMock()
        
        # All calls to primary model fail, fallback succeeds
        main_exception = Exception("Connection error")
        mock_client_instance.chat.side_effect = [
            main_exception,
            main_exception,
            main_exception,
            MagicMock(message={"content": "Fallback model response"})
        ]
        
        mock_client.return_value = mock_client_instance
        
        # Act
        result = self.agent.run("Test prompt")
        
        # Assert
        assert result == "Fallback model response"
        assert mock_client_instance.chat.call_count == 4
        assert mock_time.sleep.call_count == 2  # Sleep between retries
        
        # Check that the last call used the fallback model
        last_call = mock_client_instance.chat.call_args_list[-1]
        assert last_call[1]["model"] == "llama2"
    
    @patch('packages.agents.advanced_reasoning.agents.Client')
    @patch('packages.agents.advanced_reasoning.agents.time')
    def test_agent_all_attempts_fail(self, mock_time, mock_client):
        """Test agent behavior when all attempts including fallback fail."""
        # Arrange
        mock_client_instance = MagicMock()
        
        # All calls fail including fallback
        mock_client_instance.chat.side_effect = Exception("Connection error")
        mock_client.return_value = mock_client_instance
        
        # Act
        result = self.agent.run("Test prompt")
        
        # Assert
        assert isinstance(result, dict)
        assert "error" in result
        assert "test_agent failed after 3 attempts" in result["error"]
        assert "details" in result
