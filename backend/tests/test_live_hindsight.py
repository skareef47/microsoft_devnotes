from __future__ import annotations

import os
import pytest
from app.config import get_settings
from app.memory.hindsight import HindsightClient

settings = get_settings()

SKIP_REASON = "Live Hindsight credentials (HINDSIGHT_API_KEY and HINDSIGHT_BANK_ID) not provided in environment."
has_credentials = bool(settings.HINDSIGHT_API_KEY and settings.HINDSIGHT_BANK_ID)


@pytest.mark.skipif(not has_credentials, reason=SKIP_REASON)
@pytest.mark.asyncio
async def test_live_hindsight_retain_recall_persistence():
    """
    Live End-to-End Test:
    Executes real Retain and Recall against Hindsight Cloud when credentials are configured.
    """
    client = HindsightClient()
    bank_id = settings.HINDSIGHT_BANK_ID

    test_content = "ContextIQ Phase 2 live verification test: Team uses BullMQ."
    test_query = "What queue system does the team use for background jobs?"

    # 1. Real Retain
    retain_res = await client.retain(
        bank_id=bank_id,
        content=test_content,
        category="decision",
        metadata={"test": "phase2_live_verification"},
    )
    assert retain_res is not None
    assert retain_res.get("status") == "saved"

    # 2. Real Recall
    recall_res = await client.recall(
        bank_id=bank_id,
        query=test_query,
        limit=5,
    )
    assert len(recall_res) > 0
    found = any("BullMQ" in m.get("text", "") for m in recall_res)
    assert found, "Expected to find BullMQ in live recalled memories"
