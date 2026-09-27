from __future__ import annotations

from typing import Optional
from app.config import get_settings

settings = get_settings()


class TeamBankResolver:
    """
    Resolves the authorized Hindsight memory bank for an authenticated team.
    
    IMPORTANT TEAM MEMORY RULE:
    The MVP uses a shared team Hindsight memory bank.
    The frontend must NEVER be allowed to select an arbitrary bank.
    
    Flow:
    JWT → Authenticated User → Team Membership → Server-Controlled team_id → Authorized bank_id
    """

    def __init__(self, default_bank_id: Optional[str] = None):
        self._default_bank_id = default_bank_id or settings.HINDSIGHT_BANK_ID

    def get_authorized_bank(self, team_id: Optional[str] = None) -> str:
        """
        Derive server-controlled bank ID for team.
        Clients can never override this with an arbitrary bank parameter.
        """
        # In MVP, the server configuration dictates the shared team bank
        if self._default_bank_id:
            return self._default_bank_id.strip()

        # Fallback predictable identifier for dev environments
        tid = team_id or "default"
        return f"team_bank_{tid}"


# Global resolver singleton
_resolver = TeamBankResolver()


def resolve_team_bank_id(team_id: Optional[str] = None) -> str:
    """Convenience helper for server-side team bank resolution."""
    return _resolver.get_authorized_bank(team_id)
