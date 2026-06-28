"""User authentication and management services."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from users.models.user import User
from users.repository import UserRepository


class PasswordService:
    """Bcrypt password hashing and verification."""

    _context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def hash(cls, password: str) -> str:
        """Return bcrypt hash of *password*."""
        return cls._context.hash(password)

    @classmethod
    def verify(cls, plain_password: str, hashed_password: str) -> bool:
        """Verify *plain_password* against the stored *hashed_password*."""
        return cls._context.verify(plain_password, hashed_password)


class JWTService:
    """JWT access / refresh token creation and decoding."""

    @staticmethod
    def create_access_token(
        subject: str | uuid.UUID | Any,
        expires_delta: timedelta | None = None,
    ) -> str:
        """Create a signed JWT access token with *subject* as `sub` claim."""
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
        )
        payload = {"sub": str(subject), "exp": expire, "type": "access"}
        return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)

    @staticmethod
    def create_refresh_token(subject: str | uuid.UUID | Any) -> str:
        """Create a signed JWT refresh token."""
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )
        payload = {"sub": str(subject), "exp": expire, "type": "refresh"}
        return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)

    @staticmethod
    def decode(token: str) -> dict:
        """Decode and verify a JWT. Raises jose.JWTError on failure."""
        return jwt.decode(
            token, settings.secret_key, algorithms=[settings.jwt_algorithm]
        )


class UserService:
    """Business logic for user registration and authentication."""

    @staticmethod
    async def create(
        session: AsyncSession, *, email: str, password: str
    ) -> User:
        """Register a new user. Raises ValueError if the email is already taken."""
        if await UserRepository.get_by_email(session, email):
            raise ValueError(f"Email {email!r} is already registered.")
        user = User(email=email, hashed_password=PasswordService.hash(password))
        return await UserRepository.save(session, user)

    @staticmethod
    async def authenticate(
        session: AsyncSession, *, email: str, password: str
    ) -> User | None:
        """Return User if credentials are valid, else None."""
        user = await UserRepository.get_by_email(session, email)
        if not user or not PasswordService.verify(password, user.hashed_password):
            return None
        return user


