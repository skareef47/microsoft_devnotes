from __future__ import annotations

from typing import Any, Dict, List
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/demo", tags=["Demo"])

# Deterministic demo memory seed dataset per Section 13 of ContextIQ PRD
SYNTHETIC_DEMO_SEEDS = [
    {
        "category": "preference",
        "text": "The team uses PostgreSQL for transactional application data.",
    },
    {
        "category": "architecture",
        "text": "The team uses FastAPI for backend services.",
    },
    {
        "category": "decision",
        "text": "The team standardized on BullMQ for background jobs.",
    },
    {
        "category": "incident",
        "text": "A previous background-job implementation created operational issues, leading the team to standardize on BullMQ.",
    },
]


class SeedResponse(BaseModel):
    status: str
    message: str
    seeded_count: int
    items: List[Dict[str, Any]]


@router.post("/seed", response_model=SeedResponse, summary="Seed deterministic demo memories into Hindsight")
async def seed_demo_memories():
    """
    Seed fixed deterministic engineering context memories.
    (Activated in Phase 2 with Hindsight Retain).
    """
    return SeedResponse(
        status="prepared",
        message="Demo seed dataset prepared. Will retain into Hindsight bank in Phase 2.",
        seeded_count=len(SYNTHETIC_DEMO_SEEDS),
        items=SYNTHETIC_DEMO_SEEDS,
    )
