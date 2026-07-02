"""SQLAdmin view for CVDocument."""
from __future__ import annotations

from markupsafe import Markup
from sqladmin import ModelView

from cv_uploader.models.cv_document import CVDocument


class CVDocumentAdmin(ModelView, model=CVDocument):
    name = "CV Document"
    name_plural = "CV Documents"
    icon = "fa-solid fa-file-pdf"

    column_list = [
        CVDocument.id,
        CVDocument.candidate_id,
        CVDocument.status,
        CVDocument.uploaded_at,
    ]
    column_sortable_list = [CVDocument.uploaded_at, CVDocument.status]
    column_filters = [CVDocument.status, CVDocument.candidate_id]

    # Render a clickable link to the PDF served via /uploads static mount.
    # file_path is stored as "cvs/<candidate_id>/<uuid>.pdf" relative to
    # settings.cv_upload_dir, which is mounted at /uploads.
    column_formatters = {
        "file_path": lambda m, _: Markup(
            f'<a href="/uploads/{m.file_path}" target="_blank" '
            f'rel="noopener noreferrer">Open PDF</a>'
        )
    }
    column_formatters_detail = {
        "file_path": lambda m, _: Markup(
            f'<a href="/uploads/{m.file_path}" target="_blank" '
            f'rel="noopener noreferrer">Open PDF</a>'
        )
    }

    # Documents are created exclusively through the API.
    can_create = False
    can_edit = False
    can_delete = True
