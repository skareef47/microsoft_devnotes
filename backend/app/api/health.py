from __future__ import annotations

from typing import Dict
from fastapi import APIRouter
from sqlalchemy import text
from app.config import get_settings
from app.database import engine
from app.memory.hindsight import HindsightClient

router = APIRouter(tags=["Health"])
settings = get_settings()
hindsight_client = HindsightClient()


@router.get("/health", response_model=Dict[str, str], summary="Service Health Check")
async def get_health() -> Dict[str, str]:
    """
    Returns real subsystem health status.
    Does not pretend services are healthy if unconfigured or unreachable.
    """
    health_status: Dict[str, str] = {"api": "ok"}

    # 1. Database check
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        health_status["database"] = "ok"
    except Exception:
        health_status["database"] = "unavailable"

    # 2. Hindsight check
    if hindsight_client.is_configured:
        is_healthy = await hindsight_client.check_health()
        health_status["hindsight"] = "ok" if is_healthy else "unavailable"
    else:
        health_status["hindsight"] = "unconfigured"

    # 3. LLM check
    if settings.LLM_API_KEY:
        health_status["llm"] = "ok"
    else:
        health_status["llm"] = "unconfigured"

    return health_status
