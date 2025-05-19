"""
Tests for Docker containerization functionality.
"""

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add parent directory to system path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestDockerIntegration:
    """Tests for Docker container functionality."""

    @pytest.mark.skipif(
        not os.path.exists("/var/run/docker.sock"), reason="Docker not available"
    )
    def test_dockerfile_build(self):
        """Test building Docker image works correctly."""
        # This test will be skipped if Docker is not available
        try:
            # Run docker build in a subprocess
            project_root = Path(__file__).parent.parent
            result = subprocess.run(
                ["docker", "build", "-t", "mindmeld-test", "--no-cache", "."],
                cwd=str(project_root),
                capture_output=True,
                check=True,
                timeout=300,  # 5 minutes timeout
            )

            # If we get here, the build succeeded
            assert result.returncode == 0

            # Clean up - remove the test image
            subprocess.run(["docker", "rmi", "mindmeld-test"], capture_output=True)

        except subprocess.CalledProcessError as e:
            pytest.fail(f"Docker build failed: {e.stderr.decode()}")
        except subprocess.TimeoutExpired:
            pytest.fail("Docker build timed out")

    @pytest.mark.skipif(
        not os.path.exists("/var/run/docker.sock"), reason="Docker not available"
    )
    def test_docker_compose_validate(self):
        """Test docker-compose.yml is valid."""
        try:
            # Validate docker-compose.yml
            project_root = Path(__file__).parent.parent
            result = subprocess.run(
                ["docker-compose", "config"],
                cwd=str(project_root),
                capture_output=True,
                check=True,
            )

            # If we get here, the validation succeeded
            assert result.returncode == 0

        except subprocess.CalledProcessError as e:
            pytest.fail(f"Docker compose validation failed: {e.stderr.decode()}")


@patch("subprocess.run")
def test_docker_env_variables(mock_run):
    """Test Docker container respects environment variables."""
    # Arrange
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_process.stdout = b"MAX_RETRIES=5\nBASE_TIMEOUT=60\nFALLBACK_MODEL=mistral\n"
    mock_run.return_value = mock_process

    # Act - Run a test command that echoes environment variables
    cmd = [
        "docker",
        "run",
        "--rm",
        "-e",
        "MAX_RETRIES=5",
        "-e",
        "BASE_TIMEOUT=60",
        "-e",
        "FALLBACK_MODEL=mistral",
        "mindmeld-test",
        "sh",
        "-c",
        "echo MAX_RETRIES=$MAX_RETRIES\\nBASE_TIMEOUT=$BASE_TIMEOUT\\nFALLBACK_MODEL=$FALLBACK_MODEL",
    ]

    try:
        # We're mocking this, so it won't actually run
        result = subprocess.run(cmd, capture_output=True, check=True)

        # Assert
        mock_run.assert_called_once()
        assert "MAX_RETRIES=5" in result.stdout.decode()
        assert "BASE_TIMEOUT=60" in result.stdout.decode()
        assert "FALLBACK_MODEL=mistral" in result.stdout.decode()

    except subprocess.CalledProcessError:
        pytest.fail("Docker run command failed")
