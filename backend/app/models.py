from __future__ import annotations

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from app.database import Base


def generate_uuid(prefix: str = "id") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: generate_uuid("user"))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    team_id = Column(String, default="team_default", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Team(Base):
    __tablename__ = "teams"

    id = Column(String, primary_key=True, default="team_default")
    name = Column(String, default="ContextIQ Engineering Team", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: generate_uuid("conv"))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    team_id = Column(String, default="team_default", nullable=False)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
