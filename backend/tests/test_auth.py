from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_auth_registration_and_login():
    """Verify user registration and subsequent login flow with JWT token issuance."""
    email = "engineer@contextiq.dev"
    password = "secure_password_123"

    # 1. Register new user
    reg_response = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Test Engineer",
        },
    )
    # Could be 201 Created or 400 if already created in previous test runs
    if reg_response.status_code == 201:
        data = reg_response.json()
        assert "access_token" in data
        assert data["email"] == email
        assert data["team_id"] == "team_default"
        assert data["token_type"] == "bearer"
    else:
        assert reg_response.status_code == 400

    # 2. Login with correct credentials
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    assert login_data["email"] == email
    token = login_data["access_token"]

    # 3. Access protected /api/auth/me
    me_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == email


def test_auth_invalid_credentials():
    """Verify login fails with HTTP 401 when given incorrect password."""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "wrong_password",
        },
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_protected_endpoints_reject_unauthenticated():
    """Verify protected endpoints return HTTP 401 Unauthorized when no token is supplied."""
    chat_res = client.post(
        "/api/chat",
        json={
            "message": "test",
            "conversation_id": "conv_unauth",
            "memory_enabled": True,
        },
    )
    assert chat_res.status_code == 401

    mem_res = client.get("/api/memories")
    assert mem_res.status_code == 401

    seed_res = client.post("/api/demo/seed")
    assert seed_res.status_code == 401
