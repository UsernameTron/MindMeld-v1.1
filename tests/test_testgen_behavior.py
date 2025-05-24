#!/usr/bin/env python3
"""
Behavior tests for the TestGeneratorAgent module.
"""

from unittest.mock import MagicMock

import pytest

from packages.agents.claude_agents.agents.test_generator import TestGeneratorAgent
from packages.agents.claude_agents.api.client import ClaudeAPIClient


@pytest.fixture
def mock_api_client():
    """Create a mock Claude API client."""
    client = MagicMock(spec=ClaudeAPIClient)

    # Create a structured mock response that mimics Claude API format
    mock_response = MagicMock()

    # Mock the content block with text
    mock_content_block = MagicMock()
    mock_content_block.type = "text"
    mock_content_block.text = """
import pytest
from unittest.mock import MagicMock

def test_user_registration_success():
    '''Test successful user registration with valid data.'''
    handler = UserRegistrationHandler(mock_user_repository)
    result, status = handler.register('testuser', 'test@example.com', 'SecurePass123!')

    assert status == 201
    assert 'id' in result
    assert result['username'] == 'testuser'
    assert result['email'] == 'test@example.com'

def test_user_registration_duplicate_username():
    '''Test error handling when trying to register with an existing username.'''
    handler = UserRegistrationHandler(mock_user_repository)
    mock_user_repository.username_exists.return_value = True

    result, status = handler.register('existinguser', 'new@example.com', 'SecurePass123!')
    assert status == 400
    assert 'error' in result
    assert 'Username already exists' in result['error']

def test_user_registration_invalid_email():
    '''Test validation failure when providing an invalid email format.'''
    handler = UserRegistrationHandler(mock_user_repository)

    result, status = handler.register('validuser', 'invalid-email', 'SecurePass123!')
    assert status == 400
    assert 'error' in result
    assert 'Invalid email format' in result['error']
"""

    # Set up the mock response structure
    mock_response.content = [mock_content_block]
    mock_response.tool_calls = None

    # Configure the client to return the mock response
    client.send_message.return_value = mock_response

    return client


@pytest.fixture
def test_generator_agent(mock_api_client):
    """Create a test generator agent with mock client."""
    return TestGeneratorAgent(
        name="test_generator",
        role="test generation specialist",
        api_client=mock_api_client,
        temperature=0.4,
    )


def test_generator_creates_tests(test_generator_agent):
    """Test that test generator agent properly creates test cases from code."""
    # Source code to generate tests for
    source_code = """
    class UserRegistrationHandler:
        def __init__(self, user_repository):
            self.user_repository = user_repository
            self.validator = UserValidator()

        def register(self, username, email, password):
            # Validate user data
            validation_result = self.validator.validate_new_user(username, email, password)
            if not validation_result['valid']:
                return {'error': validation_result['reason']}, 400

            # Check for existing user
            if self.user_repository.username_exists(username):
                return {'error': 'Username already exists'}, 400

            if self.user_repository.email_exists(email):
                return {'error': 'Email already registered'}, 400

            # Create user
            user_id = self.user_repository.create_user(username, email, password)
            return {
                'id': user_id,
                'username': username,
                'email': email
            }, 201

    class UserValidator:
        def validate_new_user(self, username, email, password):
            import re

            if not username or len(username) < 3:
                return {'valid': False, 'reason': 'Username must be at least 3 characters'}

            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$', email):
                return {'valid': False, 'reason': 'Invalid email format'}

            if len(password) < 8:
                return {'valid': False, 'reason': 'Password must be at least 8 characters'}

            return {'valid': True}
    """

    # Test generation options
    options = {"framework": "pytest", "include_mocks": True, "coverage_target": 80}

    # Process the test generation
    result = test_generator_agent.process({"code": source_code, "options": options})

    # Verify result is a dictionary with expected structure
    assert isinstance(result, dict)
    assert result["status"] == "success"
    assert "data" in result

    data = result["data"]

    # Verify test generation results
    assert "test_code" in data
    assert "tests" in data  # Backward compatibility
    assert isinstance(data["test_code"], str)
    assert len(data["test_code"].strip()) > 0

    # Check that the generated test contains expected content
    test_code = data["test_code"]
    assert "import pytest" in test_code
    assert "def test_" in test_code  # Should contain test functions
    assert (
        "UserRegistrationHandler" in test_code or "test_user_registration" in test_code
    )

    # Verify additional analysis results
    assert "fixtures" in data
    assert "coverage_estimate" in data
    assert "untested_paths" in data
    assert isinstance(data["fixtures"], dict)
    assert isinstance(data["coverage_estimate"], (int, float))
    assert isinstance(data["untested_paths"], list)
