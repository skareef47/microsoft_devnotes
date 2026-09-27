from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from app.config import get_settings
from app.agent.retention_gate import evaluate_retention
from app.agent.context import build_augmented_prompt
from app.llm.provider import get_llm_provider
from app.memory.hindsight import HindsightClient, HindsightError

logger = logging.getLogger("contextiq.orchestrator")
settings = get_settings()


class AgentOrchestrator:
    """
    Coordinates the core ContextIQ request flow:
    1. Evaluates message with retention gate for durable context.
    2. Retains into Hindsight if durable signals exist.
    3. Recalls relevant team memories from Hindsight (if memory_enabled).
    4. Handles degraded mode seamlessly if Hindsight is unavailable.
    5. Builds augmented context prompt.
    6. Generates LLM response.
    7. Returns response with memories_used, memories_stored, and memory_status.
    """

    def __init__(self, hindsight_client: Optional[HindsightClient] = None):
        self.llm = get_llm_provider(settings)
        self.hindsight = hindsight_client or HindsightClient()

    async def process_chat(
        self,
        message: str,
        conversation_id: str,
        memory_enabled: bool,
        team_id: str,
        bank_id: str,
    ) -> Dict[str, Any]:
        """Execute the end-to-end chat pipeline."""
        memories_stored: List[Dict[str, Any]] = []
        memories_used: List[Dict[str, Any]] = []
        memory_status = "available" if memory_enabled else "disabled"
        degraded_warning: Optional[str] = None

        # 1. Retention Gate (detect durable engineering context)
        should_retain, signal = evaluate_retention(message)
        if should_retain:
            try:
                retain_res = await self.hindsight.retain(
                    bank_id=bank_id,
                    content=message,
                    category=signal,
                    metadata={"conversation_id": conversation_id, "team_id": team_id},
                )
                memories_stored.append({
                    "id": retain_res.get("id", "retained"),
                    "category": signal,
                    "text": message,
                    "status": "saved",
                })
            except Exception as e:
                logger.warning("Hindsight Retain failed in degraded mode: %s", type(e).__name__)
                memories_stored.append({
                    "id": "not_saved",
                    "category": signal,
                    "text": message,
                    "status": "not_saved",
                })

        # 2. Hindsight Recall (if memory_enabled)
        if memory_enabled:
            try:
                recalled = await self.hindsight.recall(
                    bank_id=bank_id,
                    query=message,
                    limit=5,
                )
                memories_used = recalled[:5] if recalled else []
                memory_status = "available"
            except Exception as e:
                # Degraded mode: one retry was already attempted by adapter
                logger.warning("Hindsight Recall failed, entering degraded mode: %s", type(e).__name__)
                memories_used = []
                memory_status = "unavailable"
                degraded_warning = "Memory temporarily unavailable — answering without persistent memory."
        else:
            memories_used = []
            memory_status = "disabled"

        # 3. Context Assembly
        augmented_prompt = build_augmented_prompt(
            user_query=message,
            recalled_memories=memories_used if memory_enabled else None,
        )

        # 4. LLM Generation
        response_text = await self.llm.generate(augmented_prompt)

        # In degraded mode, provide clear feedback if requested
        if degraded_warning and not response_text:
            response_text = degraded_warning

        return {
            "response": response_text,
            "memory_enabled": memory_enabled,
            "memories_used": memories_used,
            "memories_stored": memories_stored,
            "memory_status": memory_status,
        }
