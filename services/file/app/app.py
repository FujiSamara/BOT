from contextlib import asynccontextmanager
from fastapi import FastAPI

from common.logging import logger
from common.config import generate

from app.container import Container
from app.infra.config import Settings
from app.controllers import api
from app.controllers import admin


def create_lifespan(container: Container):
    @asynccontextmanager
    async def lifespan(_):
        try:
            awaitable = container.init_resources()
            if awaitable is not None:
                await awaitable
            yield
        finally:
            awaitable = container.shutdown_resources()
            if awaitable is not None:
                await awaitable

    return lifespan


def create_app() -> FastAPI:
    settings = generate(Settings, logger)
    container = Container(logger=logger)
    container.config.from_pydantic(settings)
    container.wire(modules=["app.controllers.admin.main", "app.app"])

    app = FastAPI(redoc_url=None, docs_url=None, lifespan=create_lifespan(container))
    app.container = container

    admin.register_admin(
        app,
        username=settings.admin_username,
        password=settings.admin_password,
    )
    app.mount("/api", api.create_api())

    return app


app = create_app()
