"""Startup routine: ensure a superuser account exists."""
from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.db import AsyncSessionLocal
from users.models.user import User
from users.repository import UserRepository
from users.services import hash_password

logger = logging.getLogger(__name__)


async def create_superuser_if_missing() -> None:
    """Create the initial superuser from env vars if no superuser exists yet."""
    async with AsyncSessionLocal() as session:
        existing = await UserRepository.get_by_email(
            session, settings.first_superuser_email
        )
        if existing:
            logger.info("Superuser already exists — skipping creation.")
            return

        user = User(
            email=settings.first_superuser_email,
            hashed_password=hash_password(settings.first_superuser_password),
            is_active=True,
            is_superuser=True,
        )
        await UserRepository.save(session, user)
        logger.info("Superuser created: %s", settings.first_superuser_email)
