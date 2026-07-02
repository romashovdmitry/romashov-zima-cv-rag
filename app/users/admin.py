"""SQLAdmin views and authentication backend for User and UserProfile."""
from __future__ import annotations

from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.db import AsyncSessionLocal
from users.models.user import User
from users.models.user_profile import UserProfile
from users.services import authenticate_user


class AdminAuthBackend(AuthenticationBackend):
    """Session-cookie auth for the admin panel.

    Only superusers can log in.
    """

    async def authenticate(self, request: Request) -> bool | RedirectResponse:
        token = request.session.get("admin_user_id")
        if token:
            return True
        return RedirectResponse(request.url_for("admin:login"), status_code=302)

    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = str(form.get("username", ""))
        password = str(form.get("password", ""))

        async with AsyncSessionLocal() as session:
            user = await authenticate_user(
                session, email=email, password=password
            )

        if user and user.is_superuser and not user.is_deleted:
            request.session["admin_user_id"] = str(user.id)
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True


authentication_backend = AdminAuthBackend(secret_key=settings.secret_key)


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

    column_list = [
        User.id,
        User.email,
        User.is_active,
        User.is_superuser,
        User.created_at,
        User.deleted_at,
    ]
    column_searchable_list = [User.email]
    column_sortable_list = [User.created_at, User.email, User.is_active]
    column_filters = [User.is_active, User.is_superuser, User.deleted_at]

    # Never expose the hashed password in the form
    form_excluded_columns = [User.hashed_password]
    column_details_exclude_list = [User.hashed_password]

    can_delete = True


class UserProfileAdmin(ModelView, model=UserProfile):
    name = "User Profile"
    name_plural = "User Profiles"
    icon = "fa-solid fa-id-card"

    column_list = [
        UserProfile.id,
        UserProfile.user_id,
        UserProfile.is_ready_to_relocate,
        UserProfile.can_work_b2b,
    ]
    column_sortable_list = [UserProfile.user_id]
    column_filters = [UserProfile.is_ready_to_relocate, UserProfile.can_work_b2b]

    can_delete = True
