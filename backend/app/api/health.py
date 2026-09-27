from __future__ import annotations

from typing import Dict
from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=Dict[str, str], summary="Service Health Check")
def get_health() -> Dict[str, str]:
    """
    Returns API health status.
    Per Phase 1 requirements:
    Initial response returns {"api": "ok"}.
    Hindsight, database, and LLM statuses will be checked once connected in Phase 2.
    """
    return {"api": "ok"}
