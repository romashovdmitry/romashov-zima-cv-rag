"""CV upload router — POST /cv/upload."""
from __future__ import annotations

import asyncio
import logging
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from qdrant_client import QdrantClient
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import AsyncSessionLocal, get_db
from core.deps import get_current_active_user
from core.qdrant_engine import get_qdrant
from cv_uploader.models.cv_document import CVDocument
from cv_uploader.repository import CVDocumentRepository
from cv_uploader.schemas import CVUploadResponse
from cv_uploader.services import chunk_text, extract_text, index_cv_chunks, save_upload
from users.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()


async def _process_cv(
    doc_id: uuid.UUID,
    file_path: str,
    candidate_id: uuid.UUID,
    qdrant: QdrantClient,
) -> None:
    """Background task: extract text → chunk → index → update status."""
    async with AsyncSessionLocal() as session:
        doc = await CVDocumentRepository.get_by_id(session, doc_id)
        if not doc:
            return

        try:
            doc.status = "processing"
            await session.commit()

            text = await asyncio.to_thread(extract_text, file_path)
            chunks = await asyncio.to_thread(chunk_text, text)
            await asyncio.to_thread(index_cv_chunks, doc_id, candidate_id, chunks, qdrant)

            doc.status = "indexed"
            await session.commit()

        except Exception:
            logger.exception("CV processing failed for document %s", doc_id)
            doc.status = "failed"
            await session.commit()


@router.post(
    "/upload",
    response_model=CVUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload a PDF CV",
    description=(
        "Accepts a PDF file, saves it to disk, creates a CVDocument record, "
        "and schedules background extraction + Qdrant indexing. "
        "Returns immediately with the document_id and status='pending'."
    ),
)
async def upload_cv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    qdrant: QdrantClient = Depends(get_qdrant),
) -> CVUploadResponse:
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only PDF files are accepted.",
        )

    file_path = await save_upload(file, current_user.id)

    doc = CVDocument(
        candidate_id=current_user.id,
        file_path=file_path,
        status="pending",
    )
    doc = await CVDocumentRepository.save(session, doc)

    background_tasks.add_task(
        _process_cv,
        doc.id,
        doc.file_path,
        doc.candidate_id,
        qdrant,
    )

    return CVUploadResponse(document_id=doc.id, status=doc.status)
