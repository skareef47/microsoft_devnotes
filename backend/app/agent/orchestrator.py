from __future__ import annotations

from typing import Any, Dict, List, Optional
from app.config import get_settings
from app.agent.retention_gate import evaluate_retention
from app.agent.context import build_augmented_prompt
from app.llm.provider import get_llm_provider

settings = get_settings()


class AgentOrchestrator:
    """
    Coordinates the core ContextIQ request flow:
    1. Evaluates message with retention gate for durable context.
    2. Recalls relevant team memories from Hindsight (if memory_enabled).
    3. Builds augmented context prompt.
    4. Calls LLM provider.
    5. Returns response along with memory usage metadata.
    """

    def __init__(self):
        self.llm = get_llm_provider(settings)

    async def process_chat(
        self,
        message: str,
        conversation_id: str,
        memory_enabled: bool,
        team_id: str,
        bank_id: str,
    ) -> Dict[str, Any]:
        """
        Execute the chat pipeline.
        (Full Hindsight Retain & Recall integration will be activated in Phase 2).
        """
        # 1. Retention check (signals durable context)
        should_retain, signal = evaluate_retention(message)
        memories_stored: List[Dict[str, Any]] = []

        # 2. Hindsight Recall (placeholder prepared for Phase 2)
        memories_used: List[Dict[str, Any]] = []
        memory_status = "available"

        # 3. Context assembly
        augmented_prompt = build_augmented_prompt(
            user_query=message,
            recalled_memories=memories_used if memory_enabled else None,
        )

        # 4. LLM Generation
        response_text = await self.llm.generate(augmented_prompt)

        return {
            "response": response_text,
            "memory_enabled": memory_enabled,
            "memories_used": memories_used,
            "memories_stored": memories_stored,
            "memory_status": memory_status,
        }
