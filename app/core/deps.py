"""FastAPI reusable dependencies."""
from __future__ import annotations

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from users.models.user import User
from users.repository import UserRepository
from users.services import JWTService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate the Bearer JWT; return the matching User."""
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = JWTService.decode(token)
        if payload.get("type") != "access":
            raise credentials_exc
        sub: str | None = payload.get("sub")
        if sub is None:
            raise credentials_exc
        user_id = uuid.UUID(sub)
    except (JWTError, ValueError):
        raise credentials_exc

    user = await UserRepository.get_by_id(session, user_id)
    if user is None or user.is_deleted:
        raise credentials_exc
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Like get_current_user but additionally asserts is_active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user
