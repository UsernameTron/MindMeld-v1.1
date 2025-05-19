import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_login_returns_access_and_refresh_token():
    response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "testpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_refresh_token_issues_new_access_token():
    # First, login to get refresh token
    login_resp = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "testpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    refresh_token = login_resp.json()["refresh_token"]
    # Use refresh token to get new access token
    refresh_resp = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_resp.status_code == 200
    data = refresh_resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_invalid_refresh_token_rejected():
    resp = client.post("/auth/refresh", json={"refresh_token": "invalidtoken"})
    assert resp.status_code == 401
    data = resp.json()
    assert "Invalid refresh token" in data["detail"]
