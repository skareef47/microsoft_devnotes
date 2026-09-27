from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.auth.passwords import hash_password, verify_password
from app.auth.jwt import create_access_token
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password with minimum 6 characters")
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


class UserProfileResponse(BaseModel):
    user_id: str
    email: str
    full_name: Optional[str] = None
    team_id: str


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user and return JWT session token",
)
def register(req: UserRegisterRequest, db: Session = Depends(get_db)):
    """
    Registers a new user account with hashed password and binds to the shared team.
    Passwords are never stored in plain text.
    """
    existing_user = db.query(User).filter(User.email == req.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    hashed_pw = hash_password(req.password)
    user = User(
        email=req.email.lower(),
        hashed_password=hashed_pw,
        full_name=req.full_name,
        team_id="team_default",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(
        {
            "sub": user.id,
            "user_id": user.id,
            "email": user.email,
            "team_id": user.team_id,
        }
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        team_id=user.team_id,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user and return JWT session token",
)
def login(req: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates user credentials against the bcrypt password hash.
    Returns signed JWT access token upon successful authentication.
    """
    user = db.query(User).filter(User.email == req.email.lower()).first()
    if not user or not user.hashed_password or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        {
            "sub": user.id,
            "user_id": user.id,
            "email": user.email,
            "team_id": user.team_id,
        }
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        team_id=user.team_id,
    )


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get authenticated user profile",
)
def get_me(current_user: User = Depends(get_current_user)):
    """Return profile for currently authenticated user."""
    return UserProfileResponse(
        user_id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        team_id=current_user.team_id,
    )
