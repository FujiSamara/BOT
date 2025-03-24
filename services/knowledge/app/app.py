from contextlib import asynccontextmanager
from fastapi import FastAPI

from common.logging import logger
from common.config import generate

from app.container import Container
from app.infra.config import Settings
from app.controllers import api


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
    settings: Settings = generate(Settings, logger)
    container = Container(logger=logger)
    container.config.from_pydantic(settings)
    container.postgres_dish_container.container.config.override(
        {"psql_dsn": settings.dish_psql_dsn, "psql_schema": settings.dish_psql_schema}
    )
    container.postgres_knowledge_container.container.config.override(
        {
            "psql_dsn": settings.knowledge_ppsql_dsn,
            "psql_schema": settings.knowledge_psql_schema,
        }
    )

    container.wire(modules=["app.controllers.api.routes.division"])

    app = FastAPI(redoc_url=None, docs_url=None, lifespan=create_lifespan(container))
    app.container = container

    app.mount("/api", api.create_api())

    return app


app = create_app()
