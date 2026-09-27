from __future__ import annotations

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter(tags=["Chat"])


class MemoryItem(BaseModel):
    id: str
    category: str
    text: str


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
async def chat_endpoint(req: ChatRequest):
    """
    Chat endpoint structure prepared for Phase 2 integration.
    Connects to AgentOrchestrator in Phase 2.
    """
    return ChatResponse(
        response="ContextIQ Phase 1 foundation is operational. Chat processing activates in Phase 2.",
        memory_enabled=req.memory_enabled,
        memories_used=[],
        memories_stored=[],
        memory_status="available",
    )
