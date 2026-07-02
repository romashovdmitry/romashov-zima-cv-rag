"""CVDocument repository — all database operations for the CVDocument model."""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cv_uploader.models.cv_document import CVDocument


class CVDocumentRepository:
    """Low-level CRUD access for CVDocument rows."""

    @staticmethod
    async def save(session: AsyncSession, doc: CVDocument) -> CVDocument:
        """Persist *doc* and return the refreshed instance."""
        session.add(doc)
        await session.commit()
        await session.refresh(doc)
        return doc

    @staticmethod
    async def get_by_id(
        session: AsyncSession, doc_id: uuid.UUID
    ) -> CVDocument | None:
        """Return CVDocument by PK."""
        result = await session.execute(
            select(CVDocument).where(CVDocument.id == doc_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_candidate(
        session: AsyncSession, candidate_id: uuid.UUID
    ) -> list[CVDocument]:
        """Return all documents for a given candidate, newest first."""
        result = await session.execute(
            select(CVDocument)
            .where(CVDocument.candidate_id == candidate_id)
            .order_by(CVDocument.uploaded_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def update_status(
        session: AsyncSession, doc: CVDocument, status: str
    ) -> CVDocument:
        """Update processing status in-place and persist."""
        doc.status = status
        session.add(doc)
        await session.commit()
        await session.refresh(doc)
        return doc
