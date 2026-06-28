"""User repository — all database operations for the User model."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from users.models.user import User


class UserRepository:
    """Low-level CRUD access for User rows."""

    @staticmethod
    async def get_by_id(
        session: AsyncSession, user_id: uuid.UUID, *, include_deleted: bool = False
    ) -> User | None:
        """Return User by PK. Soft-deleted users are excluded by default."""
        stmt = select(User).where(User.id == user_id)
        if not include_deleted:
            stmt = stmt.where(User.deleted_at.is_(None))
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(
        session: AsyncSession, email: str, *, include_deleted: bool = False
    ) -> User | None:
        """Return User by email. Soft-deleted users are excluded by default."""
        stmt = select(User).where(User.email == email)
        if not include_deleted:
            stmt = stmt.where(User.deleted_at.is_(None))
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def save(session: AsyncSession, user: User) -> User:
        """Persist *user* and return the refreshed instance."""
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def delete(session: AsyncSession, user: User) -> None:
        """Hard-delete: permanently remove the row (and its profile via CASCADE)."""
        await session.delete(user)
        await session.commit()

    @staticmethod
    async def soft_delete(session: AsyncSession, user: User) -> User:
        """Stamp deleted_at; the row stays in the DB."""
        user.deleted_at = datetime.now(timezone.utc)
        return await UserRepository.save(session, user)
