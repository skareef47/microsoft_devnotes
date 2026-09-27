from __future__ import annotations

import logging
from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel
from app.memory.bank_resolver import resolve_team_bank_id
from app.memory.hindsight import HindsightClient

logger = logging.getLogger("contextiq.api.memories")
router = APIRouter(tags=["Memories"])
hindsight_client = HindsightClient()


class MemoryRecord(BaseModel):
    id: str
    category: str
    text: str
    created_at: Optional[str] = None


class MemoriesResponse(BaseModel):
    team_id: str
    bank_id: str
    count: int
    memories: List[MemoryRecord]
    status: str = "available"


@router.get("/memories", response_model=MemoriesResponse, summary="List accessible team memories from Hindsight")
async def list_memories():
    """
    Read-only memory inspection endpoint for current team's authorized Hindsight bank.
    Server strictly controls team and bank ID. Memories are never duplicated in PostgreSQL.
    """
    team_id = "team_default"
    bank_id = resolve_team_bank_id(team_id)

    if not hindsight_client.is_configured:
        return MemoriesResponse(
            team_id=team_id,
            bank_id=bank_id,
            count=0,
            memories=[],
            status="unconfigured",
        )

    try:
        raw_memories = await hindsight_client.list_memories(bank_id=bank_id)
        records = [MemoryRecord(**m) for m in raw_memories]
        return MemoriesResponse(
            team_id=team_id,
            bank_id=bank_id,
            count=len(records),
            memories=records,
            status="available",
        )
    except Exception as e:
        logger.warning("Failed to list memories from Hindsight: %s", type(e).__name__)
        return MemoriesResponse(
            team_id=team_id,
            bank_id=bank_id,
            count=0,
            memories=[],
            status="unavailable",
        )
