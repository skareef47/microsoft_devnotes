from __future__ import annotations

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import get_settings

settings = get_settings()

# Configure engine arguments based on driver
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dependency for providing transactional database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables and default team."""
    import app.models as models  # ensure models are registered
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        team = db.query(models.Team).filter(models.Team.id == "team_default").first()
        if not team:
            team = models.Team(id="team_default", name="ContextIQ Engineering Team")
            db.add(team)
            db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()

