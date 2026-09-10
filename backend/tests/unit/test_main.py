from __future__ import annotations

from src.main import app


def test_app_exists():
    assert app is not None


def test_health_endpoint():
    from fastapi.testclient import TestClient

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
