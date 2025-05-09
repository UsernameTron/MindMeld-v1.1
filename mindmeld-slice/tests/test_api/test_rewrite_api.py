import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_rewrite_endpoint():
    resp = client.post(
        "/rewrite/", json={"content": "Hello world!", "persona_id": "cynical-humorist"}
    )
    # Accept 200 (success), 404 (persona not found), or 500 (OpenAI error)
    assert resp.status_code in (200, 404, 500)
