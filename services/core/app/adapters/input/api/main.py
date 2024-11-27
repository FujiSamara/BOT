from fastapi import FastAPI
import sys

from app.infra.logging import logger

from app.adapters.input.api.configure import configure


def create(app: FastAPI) -> FastAPI:
    api = FastAPI(docs_url=None, redoc_url=None)
    try:
        configure(api)
    except Exception as e:
        logger.critical(f"Api configuring is failed: {e}")
        sys.exit()
    logger.info("Api created")
    app.mount(path="/api", app=api)
    return api
