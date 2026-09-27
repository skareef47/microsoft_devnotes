from __future__ import annotations

from app.config import get_settings

settings = get_settings()


def resolve_team_bank_id(team_id: str) -> str:
    """
    Server-controlled team-to-bank resolution.
    
    IMPORTANT TEAM MEMORY RULE:
    The MVP uses a shared team Hindsight memory bank.
    The frontend must NEVER be allowed to select an arbitrary bank.
    
    Flow:
    JWT -> Authenticated User -> Team Membership -> Server-controlled team_id -> Authorized bank_id
    """
    # For MVP shared team memory bank, resolve server-side via environment or mapping
    configured_bank = settings.HINDSIGHT_BANK_ID
    if configured_bank:
        return configured_bank
    return f"bank_team_{team_id}"
