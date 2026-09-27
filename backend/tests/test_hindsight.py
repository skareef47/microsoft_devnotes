from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.memory.hindsight import HindsightClient, HindsightError, HindsightAuthError, HindsightUnavailableError
from app.memory.bank_resolver import TeamBankResolver, resolve_team_bank_id
from app.agent.orchestrator import AgentOrchestrator


@pytest.mark.asyncio
async def test_retain_request_success():
    """Test 1 — Retain: Verify retain sends properly formatted request to Hindsight and normalizes response."""
    client = HindsightClient(api_key="test_key_hindsight", base_url="https://api.hindsight.test")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = b'{"id": "mem_456", "status": "stored"}'
    mock_resp.json.return_value = {"id": "mem_456", "status": "stored"}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        result = await client.retain(
            bank_id="team_bank_alpha",
            content="The team standardized on BullMQ for background jobs.",
            category="decision",
        )

        assert mock_post.called
        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["json"]["content"] == "The team standardized on BullMQ for background jobs."
        assert "decision" in call_kwargs["json"]["tags"]
        assert result["id"] == "mem_456"
        assert result["category"] == "decision"
        assert result["status"] == "saved"


@pytest.mark.asyncio
async def test_recall_request_success():
    """Test 2 — Recall: Verify recall queries Hindsight with query and limit, and returns normalized items."""
    client = HindsightClient(api_key="test_key_hindsight", base_url="https://api.hindsight.test")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "results": [
            {
                "id": "mem_bullmq_1",
                "text": "The team standardized on BullMQ for background jobs.",
                "category": "decision",
                "score": 0.94,
            }
        ]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        results = await client.recall(
            bank_id="team_bank_alpha",
            query="What queue system does our team use?",
            limit=5,
        )

        assert mock_post.called
        assert len(results) == 1
        assert results[0]["id"] == "mem_bullmq_1"
        assert results[0]["category"] == "decision"
        assert "BullMQ" in results[0]["text"]


def test_bank_resolution_server_side_enforcement():
    """Test 3 — Bank Resolution: Backend strictly uses server-configured bank, client cannot override."""
    resolver = TeamBankResolver(default_bank_id="server_configured_bank_123")
    
    # Regardless of what team or client requests, server controls the authorized bank
    bank = resolver.get_authorized_bank("arbitrary_team_id")
    assert bank == "server_configured_bank_123"

    # Global convenience helper test
    resolved = resolve_team_bank_id("client_supplied_team")
    assert resolved is not None


@pytest.mark.asyncio
async def test_memory_disabled_skips_recall():
    """Test 4 — Memory Disabled: When memory_enabled is False, Hindsight recall is completely skipped."""
    mock_hindsight = MagicMock(spec=HindsightClient)
    mock_hindsight.recall = AsyncMock(return_value=[])
    mock_hindsight.retain = AsyncMock(return_value={"id": "mem_1", "status": "saved"})

    orchestrator = AgentOrchestrator(hindsight_client=mock_hindsight)

    result = await orchestrator.process_chat(
        message="What queue system should we use for email jobs?",
        conversation_id="conv_test_1",
        memory_enabled=False,
        team_id="team_alpha",
        bank_id="bank_alpha",
    )

    # Recall must NOT be called when memory is disabled
    assert not mock_hindsight.recall.called
    assert result["memory_enabled"] is False
    assert result["memories_used"] == []
    assert result["memory_status"] == "disabled"


@pytest.mark.asyncio
async def test_hindsight_failure_enters_degraded_mode():
    """Test 5 — Hindsight Failure: When Hindsight is unavailable, chat proceeds safely in degraded mode."""
    mock_hindsight = MagicMock(spec=HindsightClient)
    mock_hindsight.recall = AsyncMock(side_effect=HindsightUnavailableError("Connection timed out"))
    mock_hindsight.retain = AsyncMock(side_effect=HindsightUnavailableError("Connection timed out"))

    orchestrator = AgentOrchestrator(hindsight_client=mock_hindsight)

    result = await orchestrator.process_chat(
        message="Our architecture standardizes on PostgreSQL.",
        conversation_id="conv_test_2",
        memory_enabled=True,
        team_id="team_alpha",
        bank_id="bank_alpha",
    )

    # Request does not crash and returns response with degraded status
    assert result["memory_status"] == "unavailable"
    assert result["memories_used"] == []
    assert len(result["memories_stored"]) == 1
    assert result["memories_stored"][0]["status"] == "not_saved"
    assert result["response"] is not None


@pytest.mark.asyncio
async def test_persistence_retain_then_recall_cycle():
    """Test 6 — Persistence: Retain followed by separate Recall against Hindsight adapter."""
    client = HindsightClient(api_key="test_key_hindsight", base_url="https://api.hindsight.test")

    retain_resp = MagicMock()
    retain_resp.status_code = 200
    retain_resp.content = b'{"id": "mem_persisted_99"}'
    retain_resp.json.return_value = {"id": "mem_persisted_99"}

    recall_resp = MagicMock()
    recall_resp.status_code = 200
    recall_resp.json.return_value = {
        "results": [
            {
                "id": "mem_persisted_99",
                "text": "The team uses FastAPI for backend services.",
                "category": "architecture",
            }
        ]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        # 1. First operation: Retain
        mock_post.return_value = retain_resp
        stored = await client.retain(
            bank_id="team_bank_alpha",
            content="The team uses FastAPI for backend services.",
            category="architecture",
        )
        assert stored["id"] == "mem_persisted_99"

        # 2. Second separate operation: Recall
        mock_post.return_value = recall_resp
        recalled = await client.recall(
            bank_id="team_bank_alpha",
            query="What framework do we use for backend services?",
        )
        assert len(recalled) == 1
        assert recalled[0]["id"] == "mem_persisted_99"
        assert "FastAPI" in recalled[0]["text"]
