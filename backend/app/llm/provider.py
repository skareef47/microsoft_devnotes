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
        return (
            "This is a response from ContextIQ. "
            "Configure LLM_API_KEY in .env to connect to your live LLM provider."
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
