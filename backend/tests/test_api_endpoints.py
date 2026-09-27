from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app
from app.auth.jwt import create_access_token
from app.memory.hindsight import HindsightUnavailableError

client = TestClient(app)

# Helper fixture for authenticated calls
AUTH_TOKEN = create_access_token(
    {
        "sub": "test_engineer_1",
        "user_id": "test_engineer_1",
        "email": "test@contextiq.dev",
        "team_id": "team_default",
    }
)
AUTH_HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"}


def test_chat_endpoint_with_memory_enabled():
    """Verify POST /api/chat processes message and returns structured memory metadata."""
    payload = {
        "message": "We standardized on BullMQ for background jobs.",
        "conversation_id": "conv_e2e_1",
        "memory_enabled": True,
    }

    mock_recalled = [
        {
            "id": "mem_1",
            "category": "decision",
            "text": "The team standardized on BullMQ for background jobs.",
        }
    ]

    with patch("app.memory.hindsight.HindsightClient.retain", new_callable=AsyncMock) as mock_retain, \
         patch("app.memory.hindsight.HindsightClient.recall", new_callable=AsyncMock) as mock_recall:
        mock_retain.return_value = {"id": "mem_1", "category": "decision", "text": payload["message"], "status": "saved"}
        mock_recall.return_value = mock_recalled

        response = client.post("/api/chat", json=payload, headers=AUTH_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["memory_enabled"] is True
        assert len(data["memories_used"]) == 1
        assert data["memories_used"][0]["id"] == "mem_1"
        assert len(data["memories_stored"]) == 1
        assert data["memories_stored"][0]["status"] == "saved"
        assert data["memory_status"] == "available"
        assert mock_retain.called
        assert mock_recall.called


def test_chat_endpoint_with_memory_disabled():
    """Verify POST /api/chat skips recall when memory_enabled is False."""
    payload = {
        "message": "What queue should I use for this new email job?",
        "conversation_id": "conv_e2e_2",
        "memory_enabled": False,
    }

    with patch("app.memory.hindsight.HindsightClient.recall", new_callable=AsyncMock) as mock_recall:
        response = client.post("/api/chat", json=payload, headers=AUTH_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["memory_enabled"] is False
        assert data["memories_used"] == []
        assert data["memory_status"] == "disabled"
        assert not mock_recall.called


def test_transient_question_does_not_trigger_retain():
    """Verify ordinary questions are not retained into Hindsight memory."""
    payload = {
        "message": "What queue system did the ContextIQ team standardize on?",
        "conversation_id": "conv_query_1",
        "memory_enabled": True,
    }

    with patch("app.memory.hindsight.HindsightClient.retain", new_callable=AsyncMock) as mock_retain, \
         patch("app.memory.hindsight.HindsightClient.recall", new_callable=AsyncMock) as mock_recall:
        mock_recall.return_value = []
        response = client.post("/api/chat", json=payload, headers=AUTH_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["memories_stored"] == []
        assert not mock_retain.called


def test_degraded_mode_when_hindsight_unavailable():
    """Verify application gracefully responds when Hindsight is unavailable."""
    payload = {
        "message": "What queue should I use?",
        "conversation_id": "conv_degraded",
        "memory_enabled": True,
    }

    with patch("app.memory.hindsight.HindsightClient.recall", side_effect=HindsightUnavailableError("Server down")):
        response = client.post("/api/chat", json=payload, headers=AUTH_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["memory_status"] == "unavailable"
        assert data["memories_used"] == []
        assert len(data["response"]) > 0


def test_memories_endpoint():
    """Verify GET /api/memories returns team memories without client-side bank selection."""
    mock_memories = [
        {"id": "mem_db", "category": "preference", "text": "The team uses PostgreSQL."}
    ]

    with patch("app.memory.hindsight.HindsightClient.is_configured", True), \
         patch("app.memory.hindsight.HindsightClient.list_memories", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = mock_memories

        response = client.get("/api/memories", headers=AUTH_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert len(data["memories"]) == 1
        assert data["memories"][0]["id"] == "mem_db"


def test_demo_seed_endpoint():
    """Verify POST /api/demo/seed seeds fixed deterministic memories via Retain."""
    with patch("app.memory.hindsight.HindsightClient.is_configured", True), \
         patch("app.memory.hindsight.HindsightClient.list_memories", new_callable=AsyncMock) as mock_list, \
         patch("app.memory.hindsight.HindsightClient.retain", new_callable=AsyncMock) as mock_retain:
        mock_list.return_value = []
        mock_retain.return_value = {"id": "seeded_mem", "status": "saved"}

        response = client.post("/api/demo/seed", headers=AUTH_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("seeded", "partially_seeded")
        assert data["seeded_count"] == 4
        assert mock_retain.call_count == 4


def test_demo_seed_endpoint_idempotent():
    """Verify POST /api/demo/seed is idempotent and does not create duplicates when items already exist."""
    existing_items = [
        {"id": "m1", "text": "The team standardized on BullMQ for background jobs."},
        {"id": "m2", "text": "The team uses PostgreSQL for transactional application data."},
        {"id": "m3", "text": "The team uses FastAPI for backend services."},
        {"id": "m4", "text": "A previous background-job implementation caused operational issues, leading to the BullMQ decision."},
    ]
    with patch("app.memory.hindsight.HindsightClient.is_configured", True), \
         patch("app.memory.hindsight.HindsightClient.list_memories", new_callable=AsyncMock) as mock_list, \
         patch("app.memory.hindsight.HindsightClient.retain", new_callable=AsyncMock) as mock_retain:
        mock_list.return_value = existing_items

        response = client.post("/api/demo/seed", headers=AUTH_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("seeded", "partially_seeded")
        assert data["seeded_count"] == 4
        # Since all items are already present, retain should NOT be called
        assert mock_retain.call_count == 0



def test_team_isolation_enforced():
    """Verify client cannot supply arbitrary bank_id to chat endpoint."""
    payload = {
        "message": "Testing bank resolution",
        "conversation_id": "conv_iso",
        "memory_enabled": True,
        "bank_id": "attacker_bank",  # Extra field should be ignored
    }

    with patch("app.api.chat.resolve_team_bank_id") as mock_resolver, \
         patch("app.memory.hindsight.HindsightClient.recall", new_callable=AsyncMock) as mock_recall:
        mock_resolver.return_value = "contextiq-team"
        mock_recall.return_value = []

        response = client.post("/api/chat", json=payload, headers=AUTH_HEADERS)
        assert response.status_code == 200
        # Bank resolver was invoked with team_default, NOT attacker_bank
        mock_resolver.assert_called_with("team_default")
