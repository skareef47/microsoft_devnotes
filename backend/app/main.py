from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api import health, chat, memories, demo
from app.auth import routes as auth_routes

settings = get_settings()

app = FastAPI(
    title="ContextIQ API",
    description="Persistent-memory AI assistant backend powered by Hindsight Cloud",
    version="0.1.0",
)

# CORS configuration
origins = [
    settings.FRONTEND_URL,
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers under /api
app.include_router(health.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(memories.router, prefix="/api")
app.include_router(demo.router, prefix="/api")
app.include_router(auth_routes.router, prefix="/api")


@app.get("/")
def root():
    return {
        "service": "ContextIQ API",
        "status": "online",
        "docs_url": "/docs",
        "health_check": "/api/health",
    }
