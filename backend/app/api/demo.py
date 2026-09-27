from __future__ import annotations

import logging
from typing import Any, Dict, List
from fastapi import APIRouter
from pydantic import BaseModel
from app.memory.bank_resolver import resolve_team_bank_id
from app.memory.hindsight import HindsightClient

logger = logging.getLogger("contextiq.api.demo")
router = APIRouter(prefix="/demo", tags=["Demo"])
hindsight_client = HindsightClient()

# Deterministic synthetic demo memories per Section 10 of ContextIQ PRD
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
        "text": "A previous background-job implementation caused operational issues, leading to the BullMQ decision.",
    },
]


class SeedResponse(BaseModel):
    status: str
    message: str
    seeded_count: int
    bank_id: str
    items: List[Dict[str, Any]]


@router.post("/seed", response_model=SeedResponse, summary="Seed deterministic synthetic demo memories into Hindsight")
async def seed_demo_memories():
    """
    Seed fixed deterministic synthetic engineering context memories directly into Hindsight.
    These are synthetic demonstration facts, not real incidents.
    Never inserts memories into PostgreSQL.
    """
    team_id = "team_default"
    bank_id = resolve_team_bank_id(team_id)

    if not hindsight_client.is_configured:
        return SeedResponse(
            status="blocked_by_missing_credentials",
            message="Hindsight credentials (HINDSIGHT_API_KEY) are not configured in environment.",
            seeded_count=0,
            bank_id=bank_id,
            items=[],
        )

    seeded_results = []
    errors = []

    for seed in SYNTHETIC_DEMO_SEEDS:
        try:
            res = await hindsight_client.retain(
                bank_id=bank_id,
                content=seed["text"],
                category=seed["category"],
                metadata={"source": "demo_seed", "synthetic": True},
            )
            seeded_results.append({
                "id": res.get("id"),
                "category": seed["category"],
                "text": seed["text"],
                "status": "seeded",
            })
        except Exception as e:
            logger.warning("Failed to seed memory '%s': %s", seed["category"], str(e))
            errors.append(f"{seed['category']}: {type(e).__name__}")

    if errors and not seeded_results:
        return SeedResponse(
            status="failed",
            message=f"Hindsight Retain failed for all seeds: {', '.join(errors)}",
            seeded_count=0,
            bank_id=bank_id,
            items=[],
        )

    return SeedResponse(
        status="seeded" if not errors else "partially_seeded",
        message=f"Successfully seeded {len(seeded_results)} synthetic demo memories into Hindsight bank '{bank_id}'.",
        seeded_count=len(seeded_results),
        bank_id=bank_id,
        items=seeded_results,
    )
