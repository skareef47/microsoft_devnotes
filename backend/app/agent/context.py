from __future__ import annotations

from typing import Any, Dict, List, Optional

SYSTEM_PROMPT = """You are ContextIQ, a persistent-memory AI assistant for software engineering teams.
Your primary strength is that you remember the team's engineering context, architectural decisions,
technology preferences, standards, and incident history.

When relevant team memories are provided below, prioritize them to provide precise, team-aligned responses.
If memory is disabled or no relevant memories exist, provide standard high-quality technical assistance.
Never invent or fabricate team decisions or historical incidents that are not in the provided memories.
"""


def build_augmented_prompt(
    user_query: str,
    recalled_memories: Optional[List[Dict[str, Any]]] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None,
) -> str:
    """
    Assemble the LLM prompt integrating durable team memories into the conversation context.
    """
    prompt_sections = [SYSTEM_PROMPT.strip(), ""]

    if recalled_memories and len(recalled_memories) > 0:
        prompt_sections.append("### RELEVANT TEAM ENGINEERING CONTEXT (FROM HINDSIGHT MEMORY):")
        for idx, mem in enumerate(recalled_memories, 1):
            text = mem.get("text", mem.get("content", ""))
            category = mem.get("category", "engineering_context")
            prompt_sections.append(f"{idx}. [{category.upper()}] {text}")
        prompt_sections.append("")

    if conversation_history:
        prompt_sections.append("### RECENT CONVERSATION HISTORY:")
        for msg in conversation_history:
            role = msg.get("role", "user").capitalize()
            content = msg.get("content", "")
            prompt_sections.append(f"{role}: {content}")
        prompt_sections.append("")

    prompt_sections.append(f"### USER QUERY:\n{user_query}")
    return "\n".join(prompt_sections)
