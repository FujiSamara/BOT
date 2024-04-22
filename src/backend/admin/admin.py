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

class FujiAdmin(Admin):
    def __init__(self, app: Starlette, engine: Engine | None = None, session_maker: sessionmaker | async_sessionmaker | None = None, base_url: str = "/admin", title: str = "Admin", logo_url: str | None = None, middlewares: Sequence[Middleware] | None = None, debug: bool = False, templates_dir: str = "templates", authentication_backend: AuthenticationBackend | None = None) -> None:
        super().__init__(app, engine, session_maker, base_url, title, logo_url, middlewares, debug, templates_dir, authentication_backend)
    
        self.admin.add_route(
            path='/download',
            route=self.download_file,
            name="download"
        )

    @login_required
    async def download_file(self, request: Request) -> FileResponse | Response:
        '''Returns file by his path.
        '''
        path = request.query_params.get("path")
        if not Path(path).is_file():
            return Response(content="File not found", status_code=400)
        
        if not path:
            return Response(content="Path is empty", status_code=400)
        
        filename = Path(path).name

        return FileResponse(path=path, filename=filename, media_type="multipart/form-data")