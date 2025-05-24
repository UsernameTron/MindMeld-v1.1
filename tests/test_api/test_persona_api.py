from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_personas():
    resp = client.get("/personas/")
    assert resp.status_code == 200
    assert "personas" in resp.json()


def test_get_persona_not_found():
    resp = client.get("/personas/does-not-exist/")
    assert resp.status_code == 404
