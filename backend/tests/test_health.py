from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify GET /api/health returns API status ok and subsystem reports."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["api"] == "ok"
    assert "database" in data
    assert "hindsight" in data
    assert "llm" in data


def test_root_endpoint():
    """Verify root / returns API status."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "ContextIQ API"
