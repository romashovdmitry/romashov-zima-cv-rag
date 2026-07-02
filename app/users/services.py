"""User authentication and management — plain functions grouped by concern."""
from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from users.models.user import User
from users.repository import UserRepository


# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------

def _digest_password(password: str) -> bytes:
    """SHA-256 pre-hash before bcrypt to remove the 72-byte input limit."""
    return hashlib.sha256(password.encode("utf-8")).digest()


def hash_password(password: str) -> str:
    """Return a bcrypt hash of *password*."""
    return bcrypt.hashpw(_digest_password(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True when *plain_password* matches the stored *hashed_password*."""
    try:
        return bcrypt.checkpw(
            _digest_password(plain_password), hashed_password.encode("utf-8")
        )
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def create_access_token(
    subject: str | uuid.UUID | Any,
    expires_delta: timedelta | None = None,
) -> str:
    """Return a signed JWT access token."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {"sub": str(subject), "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(subject: str | uuid.UUID | Any) -> str:
    """Return a signed JWT refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    payload = {"sub": str(subject), "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    """Decode and verify a JWT. Raises jose.JWTError on failure."""
    return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])


# ---------------------------------------------------------------------------
# User business logic
# ---------------------------------------------------------------------------

async def create_user(
    session: AsyncSession, *, email: str, password: str
) -> User:
    """Register a new user. Raises ValueError if the email is already taken."""
    if await UserRepository.get_by_email(session, email):
        raise ValueError(f"Email {email!r} is already registered.")
    user = User(email=email, hashed_password=hash_password(password))
    return await UserRepository.save(session, user)


async def authenticate_user(
    session: AsyncSession, *, email: str, password: str
) -> User | None:
    """Return User if credentials are valid, else None."""
    user = await UserRepository.get_by_email(session, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
