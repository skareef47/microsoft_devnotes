from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["Authentication"])


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    team_name: Optional[str] = "Default Engineering Team"


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    team_id: str


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user and team",
)
def register(req: UserRegisterRequest):
    """Register endpoint stub prepared for Phase 2 auth implementation."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Registration endpoint will be activated in Phase 2.",
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user and return JWT session token",
)
def login(req: UserLoginRequest):
    """Login endpoint stub prepared for Phase 2 auth implementation."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication endpoint will be activated in Phase 2.",
    )
