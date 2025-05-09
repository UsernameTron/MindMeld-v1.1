import os
import sys

# Set testing flag BEFORE any app imports
from app.core.test_config import IS_TESTING

sys.modules["app.core.test_config"].IS_TESTING = True

import asyncio
import os
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.auth_middleware import APIKeyMiddleware
from app.main import app as main_app


class MockRedisClient:
    def __init__(self):
        self._store = {}
        self._expiries = {}
        self._incr_counter = {}

    async def incr(self, key):
        self._incr_counter[key] = self._incr_counter.get(key, 0) + 1
        return self._incr_counter[key]

    async def expire(self, key, ttl):
        self._expiries[key] = ttl
        return True

    async def ttl(self, key):
        return self._expiries.get(key, 60)

    async def eval(self, *args, **kwargs):
        # Return a predictable value for tests
        return 1


@pytest.fixture(scope="session")
def app_fixture() -> FastAPI:
    """Fixture for FastAPI app instance used in tests."""
    return main_app


@pytest.fixture(scope="session")
def client(app_fixture: FastAPI) -> TestClient:
    """Fixture for FastAPI TestClient."""
    return TestClient(app_fixture)


@pytest.fixture(autouse=True)
def test_env(monkeypatch):
    """Fixture to set up test environment variables or mock settings if needed."""
    # Example: monkeypatch.setenv("ENV", "test")
    # Example: monkeypatch.setattr("app.core.config.settings.LOG_LEVEL", "DEBUG")
    yield


@pytest.fixture(autouse=True)
def mock_redis():
    """Automatically patch Redis for all tests to prevent real connections."""
    with patch(
        "app.core.middleware.redis", new_callable=lambda: MockRedisClient()
    ) as mock_redis:
        yield mock_redis


@pytest.fixture(autouse=True)
def clear_api_keys_db():
    from app.services.auth.api_key_service import api_keys_db

    api_keys_db.clear()
    yield
    api_keys_db.clear()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the session."""
    import asyncio

    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def valid_jwt():
    from app.services.auth.auth_service import create_access_token

    return create_access_token(
        {"sub": "testuser", "scopes": ["analyze", "chat", "rewrite"]}
    )


@pytest.fixture
def invalid_jwt():
    return "invalid.jwt.token"


@pytest.fixture
def valid_api_key():
    return "valid-analyze-key"


@pytest.fixture
def invalid_api_key():
    return "invalid-key"


@pytest.fixture
def enforce_auth(monkeypatch):
    monkeypatch.setenv("AUTH_ENABLED", "true")
    yield


@pytest.fixture
def enforce_real_auth(monkeypatch):
    import app.core.test_config as test_config

    monkeypatch.setenv("AUTH_ENABLED", "true")
    test_config.IS_TESTING = False
    yield
    test_config.IS_TESTING = True
