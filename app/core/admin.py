"""SQLAdmin setup — assembles the admin panel and mounts it onto the app."""
from __future__ import annotations

from fastapi import FastAPI
from sqladmin import Admin

from core.db import engine
from cv_uploader.admin import CVDocumentAdmin
from users.admin import UserAdmin, UserProfileAdmin, authentication_backend


def create_admin(app: FastAPI) -> None:
    """Mount SQLAdmin onto *app* and register all model views."""
    admin = Admin(
        app,
        engine=engine,
        authentication_backend=authentication_backend,
        title="CV RAG Admin",
        base_url="/admin",
    )
    admin.add_view(UserAdmin)
    admin.add_view(UserProfileAdmin)
    admin.add_view(CVDocumentAdmin)
