from fastapi import FastAPI
from sqladmin import Admin
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from dependency_injector.wiring import Provide, inject

from app.container import Container
from common.auth import AdminAuthenticationBackend
import app.controllers.admin.views as views


@inject
def register_admin(
    app: FastAPI,
    *,
    username: str,
    password: str,
    session_maker: async_sessionmaker[AsyncSession] = Provide[Container.sessionmaker],
):
    authentication_backend = AdminAuthenticationBackend(
        username=username, password=password
    )
    admin = Admin(
        app,
        title="Knowledge panel",
        authentication_backend=authentication_backend,
        session_maker=session_maker,
    )
    admin.add_view(views.DivisionView)
    admin.add_view(views.BusinessCardView)
