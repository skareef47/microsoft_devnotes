from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import httpx
from app.config import Settings, get_settings


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate response from LLM."""
        pass


class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM provider."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        if not self.api_key:
            return "Gemini API key is not configured. Please set LLM_API_KEY."

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]


class OpenAIProvider(BaseLLMProvider):
    """OpenAI-compatible LLM provider."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        if not self.api_key:
            return "OpenAI API key is not configured. Please set LLM_API_KEY."

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


class MockLLMProvider(BaseLLMProvider):
    """Fallback / Mock LLM provider for zero-key local testing."""

    async def generate(self, prompt: str, **kwargs: Any) -> str:
        # Check if recalled team memories are present in the augmented prompt
        active_memory_marker = None
        for m in [
            "### PERSISTENT TEAM MEMORY (BACKGROUND CONTEXT):",
            "### RELEVANT TEAM ENGINEERING CONTEXT (FROM HINDSIGHT MEMORY):",
        ]:
            if m in prompt:
                active_memory_marker = m
                break

        active_user_marker = "### CURRENT USER REQUEST:" if "### CURRENT USER REQUEST:" in prompt else "### USER QUERY:"

        if active_memory_marker:
            # Memory ON with recalled context
            try:
                after_marker = prompt.split(active_memory_marker)[1]
                memory_section = after_marker.split(active_user_marker)[0].strip()
                mem_lines = [
                    line.strip()
                    for line in memory_section.splitlines()
                    if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith("-"))
                ][:3]
                summary = "\n".join(f"- {m}" for m in mem_lines)
            except Exception:
                summary = "- Team engineering decision retained in Hindsight"

            return (
                f"Based on our team's established engineering standards and recalled context:\n\n"
                f"{summary}\n\n"
                f"We recommend following this existing team standard for your task to maintain architectural consistency.\n\n"
                f"*(Generated via ContextIQ Mock Provider using real Hindsight memory)*"
            )
        else:
            # Memory OFF or no memories available - generic response
            lower_prompt = prompt.lower()
            if "queue" in lower_prompt or "job" in lower_prompt:
                topic_guidance = (
                    "When selecting a job queue system, standard industry options include RabbitMQ, "
                    "Redis-backed queues (such as BullMQ or Celery), Apache Kafka, or managed cloud queues (AWS SQS, Google Cloud Tasks). "
                    "Evaluation depends on delivery guarantees, language stack, and operational scale."
                )
            elif "database" in lower_prompt or "data" in lower_prompt:
                topic_guidance = (
                    "For database workloads, standard industry practices generally choose PostgreSQL for transactional ACID workloads, "
                    "MongoDB or DynamoDB for document stores, and Redis for caching."
                )
            else:
                topic_guidance = (
                    "ContextIQ provides technical guidance for engineering tasks. "
                    "When memory is disabled, answers are generated using general software engineering principles."
                )

            return (
                f"{topic_guidance}\n\n"
                f"*(Generated via ContextIQ Mock Provider — Memory OFF / Generic mode)*"
            )



def get_llm_provider(settings: Optional[Settings] = None) -> BaseLLMProvider:
    """Factory creating configured LLM provider based on environment settings."""
    cfg = settings or get_settings()
    provider_name = (cfg.LLM_PROVIDER or "gemini").lower()

    if not cfg.LLM_API_KEY:
        return MockLLMProvider()

    if provider_name == "gemini":
        return GeminiProvider(api_key=cfg.LLM_API_KEY, model=cfg.LLM_MODEL)
    elif provider_name in ("openai", "azure"):
        return OpenAIProvider(api_key=cfg.LLM_API_KEY, model=cfg.LLM_MODEL)
    else:
        return MockLLMProvider()
