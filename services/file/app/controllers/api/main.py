from fastapi import FastAPI

from app.controllers.api.router import router


def create_api() -> FastAPI:
    api = FastAPI()

    api.include_router(router, prefix="/file")

    return api
