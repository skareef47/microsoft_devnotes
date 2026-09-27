from __future__ import annotations

from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Memories"])


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


@router.get("/memories", response_model=MemoriesResponse, summary="List accessible team memories")
async def list_memories():
    """
    Read-only memory list endpoint for current team's authorized memory bank.
    (Activated in Phase 2).
    """
    return MemoriesResponse(
        team_id="team_default",
        bank_id="team_default_bank_id",
        count=0,
        memories=[],
    )
