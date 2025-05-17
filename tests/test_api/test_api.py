"""
Tests for the MindMeld API service.
"""
import os
import json
import time
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to system path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the API app
from api import app, check_ollama_available

# Create test client
client = TestClient(app)


@pytest.fixture
def mock_agent():
    """Mock agent for testing."""
    mock = MagicMock()
    mock.run.return_value = "Test agent response"
    return mock


@pytest.fixture
def mock_agent_factory():
    """Mock the AGENT_REGISTRY."""
    with patch("api.AGENT_REGISTRY") as mock_registry:
        # Set up the mock registry
        mock_registry.__contains__.side_effect = lambda key: key == "test_agent"
        mock_registry.keys.return_value = ["test_agent", "other_agent"]
        
        # Create a mock agent creator function
        mock_creator = MagicMock()
        mock_agent = MagicMock()
        mock_agent.run.return_value = "Test agent response"
        mock_creator.return_value = mock_agent
        
        # Configure the registry to return the mock creator
        mock_registry.__getitem__.side_effect = lambda key: mock_creator if key == "test_agent" else None
        
        yield mock_registry


@pytest.fixture
def mock_ollama_available():
    """Mock the check_ollama_available function."""
    with patch("api.check_ollama_available", return_value=True) as mock:
        yield mock


class TestAPI:
    """Tests for the MindMeld API."""

    def test_health_check_healthy(self, mock_ollama_available):
        """Test health check when Ollama is available."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["ollama_status"] is True
        assert "version" in data

    @patch("api.check_ollama_available", return_value=False)
    def test_health_check_degraded(self, mock_available):
        """Test health check when Ollama is not available."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["ollama_status"] is False
        assert "version" in data

    def test_list_agents(self, mock_agent_factory):
        """Test listing available agents."""
        response = client.get("/agents")
        
        assert response.status_code == 200
        data = response.json()
        assert data["agents"] == ["test_agent", "other_agent"]
        assert data["total"] == 2

    def test_run_agent_success(self, mock_agent_factory, mock_ollama_available):
        """Test successfully running an agent."""
        response = client.post(
            "/agents/run",
            json={"prompt": "Test prompt", "agent_name": "test_agent"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["agent"] == "test_agent"
        assert data["result"] == "Test agent response"
        assert data["status"] == "success"
        assert "execution_time" in data

    def test_run_agent_not_found(self, mock_agent_factory, mock_ollama_available):
        """Test running a non-existent agent."""
        response = client.post(
            "/agents/run",
            json={"prompt": "Test prompt", "agent_name": "nonexistent_agent"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    @patch("api.check_ollama_available", return_value=False)
    def test_run_agent_ollama_unavailable(self, mock_available, mock_agent_factory):
        """Test running an agent when Ollama is not available."""
        response = client.post(
            "/agents/run",
            json={"prompt": "Test prompt", "agent_name": "test_agent"}
        )
        
        assert response.status_code == 503
        data = response.json()
        assert "Ollama service is not available" in data["detail"]

    def test_run_agent_error(self, mock_agent_factory, mock_ollama_available):
        """Test handling errors from agents."""
        # Configure the mock agent to return an error
        mock_creator = mock_agent_factory.__getitem__.return_value
        mock_agent = mock_creator.return_value
        mock_agent.run.return_value = {"error": "Test error", "details": "Error details"}
        
        response = client.post(
            "/agents/run",
            json={"prompt": "Test prompt", "agent_name": "test_agent"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["agent"] == "test_agent"
        assert data["status"] == "error"
        assert data["result"]["error"] == "Test error"
        assert "execution_time" in data

    def test_async_run_agent(self, mock_agent_factory, mock_ollama_available):
        """Test running an agent asynchronously."""
        with patch("api.background_tasks.add_task") as mock_add_task:
            response = client.post(
                "/agents/async-run",
                json={"prompt": "Test prompt", "agent_name": "test_agent"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "job_id" in data
            assert data["status"] == "submitted"
            
            # Verify the background task was added
            mock_add_task.assert_called_once()

    def test_get_job_nonexistent(self):
        """Test getting status of a non-existent job."""
        response = client.get("/jobs/nonexistent_job")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
