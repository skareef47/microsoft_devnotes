from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from app.memory.bank_resolver import resolve_team_bank_id
from app.agent.orchestrator import AgentOrchestrator
from app.auth.dependencies import get_current_user
from app.models import User

router = APIRouter(tags=["Chat"])

# Shared orchestrator instance
orchestrator = AgentOrchestrator()


class MemoryItem(BaseModel):
    id: str
    category: str
    text: str
    created_at: Optional[str] = None
    source: Optional[str] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="The user's query or statement")
    conversation_id: str = Field(..., description="Unique conversation identifier")
    memory_enabled: bool = Field(default=True, description="Toggle for recalling Hindsight memories")


class ChatResponse(BaseModel):
    response: str
    memory_enabled: bool
    memories_used: List[MemoryItem] = []
    memories_stored: List[Dict[str, Any]] = []
    memory_status: str = "available"


@router.post("/chat", response_model=ChatResponse, summary="Send message to ContextIQ agent")
async def chat_endpoint(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Main chat endpoint coordinating the ContextIQ persistent memory pipeline.
    Server controls the team and bank ID resolution; client cannot inject an arbitrary bank.
    """
    # 1. Resolve server-side team and memory bank based on authenticated user
    team_id = current_user.team_id or "team_default"
    bank_id = resolve_team_bank_id(team_id)

    # 2. Process via orchestrator (Retain, Recall, LLM, Degraded mode)
    result = await orchestrator.process_chat(
        message=req.message,
        conversation_id=req.conversation_id,
        memory_enabled=req.memory_enabled,
        team_id=team_id,
        bank_id=bank_id,
    )

    return ChatResponse(
        response=result["response"],
        memory_enabled=result["memory_enabled"],
        memories_used=[MemoryItem(**m) for m in result["memories_used"]],
        memories_stored=result["memories_stored"],
        memory_status=result["memory_status"],
    )
