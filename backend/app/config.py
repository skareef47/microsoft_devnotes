from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """ContextIQ application configuration loaded from environment variables."""

    # Application & Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    FRONTEND_URL: str = "http://localhost:3000"

    # Database Configuration (PostgreSQL-compatible)
    # Default to local SQLite for zero-config startup, or PostgreSQL when configured
    DATABASE_URL: str = "sqlite:///./contextiq.db"

    # Authentication / JWT
    JWT_SECRET: str = "dev_secret_change_in_production_minimum_32_characters"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Memory: Self-Hosted Hindsight
    # Server-only credentials. Never exposed to frontend.
    HINDSIGHT_API_KEY: str = ""
    HINDSIGHT_BANK_ID: str = "contextiq-team"
    HINDSIGHT_BASE_URL: str = "http://localhost:8888"

    # LLM Provider Configuration
    # Supported providers: gemini, openai, anthropic, mock
    LLM_PROVIDER: str = "mock"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gemini-1.5-flash"

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()
