from fastapi import FastAPI

from app.controllers.api.router import router


def create_api() -> FastAPI:
    api = FastAPI(title="File api", version="1.0.0")

    api.include_router(router, prefix="/file")

    return api
