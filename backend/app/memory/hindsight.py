from __future__ import annotations

from typing import Any, Dict, List, Optional
import httpx
from app.config import get_settings

settings = get_settings()


class HindsightClient:
    """
    Hindsight Cloud memory client adapter.
    Handles Retain and Recall operations against the authorized team bank.
    
    Architectural boundary: Only backend interacts with Hindsight Cloud.
    Frontend NEVER has direct access.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.HINDSIGHT_API_KEY
        self.base_url = base_url or settings.HINDSIGHT_BASE_URL

    async def check_health(self) -> bool:
        """Verify connectivity to Hindsight Cloud (Phase 2)."""
        if not self.api_key:
            return False
        # Phase 2: Live connectivity check
        return False

    async def retain(
        self,
        bank_id: str,
        content: str,
        category: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Retain durable engineering context in Hindsight team bank.
        (Activated in Phase 2).
        """
        raise NotImplementedError("Hindsight Retain will be activated in Phase 2.")

    async def recall(
        self,
        bank_id: str,
        query: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Recall relevant memories from Hindsight team bank.
        (Activated in Phase 2).
        """
        raise NotImplementedError("Hindsight Recall will be activated in Phase 2.")
