from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify GET /api/health returns {'api': 'ok'}."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"api": "ok"}


def test_root_endpoint():
    """Verify root / returns API status."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "ContextIQ API"
