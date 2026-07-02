"""Pydantic schemas for the CV uploader API."""
from __future__ import annotations

import uuid

from pydantic import BaseModel


class CVUploadResponse(BaseModel):
    document_id: uuid.UUID
    status: str
