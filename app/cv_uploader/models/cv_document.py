"""CVDocument ORM model — tracks an uploaded PDF and its indexing status."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base


class CVDocument(Base):
    """One PDF uploaded by a registered candidate."""

    __tablename__ = "cv_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Only registered users can upload — hard FK, CASCADE on user deletion.
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # Path relative to settings.cv_upload_dir, e.g. "cvs/<candidate_id>/<uuid>.pdf"
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    # pending → processing → indexed | failed
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending"
    )
