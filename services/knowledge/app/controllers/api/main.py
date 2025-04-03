from fastapi import FastAPI

from app.controllers.api import routes


def create_api() -> FastAPI:
    api = FastAPI(title="Knowledge api", version="1.0.0")

    api.include_router(routes.card, prefix="/cards")
    api.include_router(routes.division, prefix="/divisions")
    api.include_router(routes.dish, prefix="/dishes")

    return api
