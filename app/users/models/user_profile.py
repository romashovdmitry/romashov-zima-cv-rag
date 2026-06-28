"""UserProfile ORM model — one-to-one additional settings for a User."""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base

if TYPE_CHECKING:
    from users.models.user import User


class UserProfile(Base):
    """One-to-one extension of User with job-search preferences."""

    __tablename__ = "user_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    is_ready_to_relocate: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        default=None,
        description="Whether the user is open to relocation for work"
    )
    can_work_b2b: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        default=None,
        description="Whether the user can work on a B2B basis"
    )

    # realationships

    user: Mapped[User] = relationship("User", back_populates="profile")
