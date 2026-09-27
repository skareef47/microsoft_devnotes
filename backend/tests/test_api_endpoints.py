from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app

client = TestClient(app)


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

        response = client.post("/api/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["memory_enabled"] is True
        assert len(data["memories_used"]) == 1
        assert data["memories_used"][0]["id"] == "mem_1"
        assert len(data["memories_stored"]) == 1
        assert data["memory_status"] == "available"


def test_chat_endpoint_with_memory_disabled():
    """Verify POST /api/chat skips recall when memory_enabled is False."""
    payload = {
        "message": "What database do we use?",
        "conversation_id": "conv_e2e_2",
        "memory_enabled": False,
    }

    with patch("app.memory.hindsight.HindsightClient.recall", new_callable=AsyncMock) as mock_recall:
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["memory_enabled"] is False
        assert data["memories_used"] == []
        assert data["memory_status"] == "disabled"
        assert not mock_recall.called


def test_memories_endpoint():
    """Verify GET /api/memories returns team memories without client-side bank selection."""
    mock_memories = [
        {"id": "mem_db", "category": "preference", "text": "The team uses PostgreSQL."}
    ]

    with patch("app.memory.hindsight.HindsightClient.is_configured", True), \
         patch("app.memory.hindsight.HindsightClient.list_memories", new_callable=AsyncMock) as mock_list:
        mock_list.return_value = mock_memories

        response = client.get("/api/memories")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert len(data["memories"]) == 1
        assert data["memories"][0]["id"] == "mem_db"


def test_demo_seed_endpoint():
    """Verify POST /api/demo/seed seeds fixed deterministic memories via Retain."""
    with patch("app.memory.hindsight.HindsightClient.is_configured", True), \
         patch("app.memory.hindsight.HindsightClient.retain", new_callable=AsyncMock) as mock_retain:
        mock_retain.return_value = {"id": "seeded_mem", "status": "saved"}

        response = client.post("/api/demo/seed")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("seeded", "partially_seeded")
        assert data["seeded_count"] == 4
        assert mock_retain.call_count == 4
