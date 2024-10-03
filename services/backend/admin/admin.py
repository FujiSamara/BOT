from typing import Sequence
from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import sessionmaker
from starlette.applications import Starlette
from starlette.middleware import Middleware
from sqladmin.authentication import login_required
from fastapi import Request
from fastapi.responses import FileResponse, Response
from pathlib import Path
from hashlib import sha256

from settings import get_settings


class FujiAdmin(Admin):
    def __init__(
        self,
        app: Starlette,
        engine: Engine | None = None,
        session_maker: sessionmaker | async_sessionmaker | None = None,
        base_url: str = "/admin",
        title: str = "Admin",
        logo_url: str | None = None,
        middlewares: Sequence[Middleware] | None = None,
        debug: bool = False,
        templates_dir: str = "templates",
        authentication_backend: AuthenticationBackend | None = None,
    ) -> None:
        super().__init__(
            app,
            engine,
            session_maker,
            base_url,
            title,
            logo_url,
            middlewares,
            debug,
            templates_dir,
            authentication_backend,
        )

        self.admin.add_route(
            path="/download", route=self.download_file, name="download"
        )

    @login_required
    async def download_file(self, request: Request) -> FileResponse | Response:
        """Returns file by his name."""
        filename = request.query_params.get("name")
        path = Path.joinpath(Path(get_settings().storage_path), Path(filename))
        if not Path(path).is_file():
            return Response(content="File not found", status_code=400)

        if not path:
            return Response(content="Path is empty", status_code=400)

        return FileResponse(
            path=path, filename=filename, media_type="multipart/form-data"
        )


class AdminAuth(AuthenticationBackend):
    """
    Authentication class for admin panel.
    """

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        if not username or not password:
            return False

        if not hasattr(self, "username"):
            self.username = username
            self.password = sha256(password.encode()).hexdigest()

        if self.username != username:
            return False

        if sha256(password.encode()).hexdigest() != self.password:
            return False

        request.session["username"] = username

        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        if not request.session:
            return False

        return True
