import pytest
from fastapi import Request

from app.services.auth.api_key_service import (
    api_keys_db,
    create_api_key,
    get_api_key_info,
    revoke_api_key,
    validate_api_key,
)
from app.services.auth.auth_service import AuthResult, AuthService


@pytest.mark.asyncio
async def test_validate_jwt_invalid_token():
    auth_service = AuthService()
    request = Request(
        scope={
            "type": "http",
            "headers": [(b"authorization", b"Bearer invalid_token")],
            "method": "GET",
        }
    )
    result = await auth_service.validate_jwt(request, required_scope="analyze")
    assert result == AuthResult.INVALID


@pytest.mark.asyncio
async def test_validate_jwt_missing_token():
    auth_service = AuthService()
    request = Request(scope={"type": "http", "headers": [], "method": "GET"})
    result = await auth_service.validate_jwt(request, required_scope="analyze")
    assert result == AuthResult.INVALID


@pytest.mark.asyncio
async def test_validate_jwt_insufficient_scope(monkeypatch):
    auth_service = AuthService()
    # Valid JWT with no scopes
    from app.services.auth.auth_service import create_access_token

    token = create_access_token({"sub": "testuser", "scopes": ["chat"]})
    request = Request(
        scope={
            "type": "http",
            "headers": [(b"authorization", f"Bearer {token}".encode())],
            "method": "GET",
        }
    )
    result = await auth_service.validate_jwt(request, required_scope="analyze")
    assert result == AuthResult.INSUFFICIENT_SCOPE


@pytest.mark.asyncio
async def test_validate_jwt_valid(monkeypatch):
    auth_service = AuthService()
    from app.services.auth.auth_service import create_access_token

    token = create_access_token({"sub": "testuser", "scopes": ["analyze"]})
    request = Request(
        scope={
            "type": "http",
            "headers": [(b"authorization", f"Bearer {token}".encode())],
            "method": "GET",
        }
    )
    result = await auth_service.validate_jwt(request, required_scope="analyze")
    assert result == AuthResult.OK


@pytest.mark.asyncio
async def test_validate_api_key_missing():
    auth_service = AuthService()
    request = Request(scope={"type": "http", "headers": [], "method": "GET"})
    result = await auth_service.validate_api_key(request, required_scope="analyze")
    assert result == AuthResult.INVALID


@pytest.mark.asyncio
async def test_validate_api_key_valid():
    auth_service = AuthService()
    request = Request(
        scope={
            "type": "http",
            "headers": [(b"x-api-key", b"valid_key")],
            "method": "GET",
        }
    )
    result = await auth_service.validate_api_key(request, required_scope="analyze")
    assert result == AuthResult.OK


def test_validate_api_key_invalid():
    assert not validate_api_key("not-a-key")


def test_validate_api_key_missing_scope():
    key = create_api_key("client1", ["read"])
    assert not validate_api_key(key, required_scope="write")


def test_get_api_key_info_missing():
    assert get_api_key_info("not-a-key") is None


def test_revoke_api_key_missing():
    assert not revoke_api_key("not-a-key")


def test_revoke_api_key_success():
    key = create_api_key("client2", ["read"])
    assert revoke_api_key(key)
    assert key not in api_keys_db
