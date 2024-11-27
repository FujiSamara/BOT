from fastapi import FastAPI
import sys

from app.infra.logging import logger

from app.adapters.input.api.auth.configure import configure


def create(app: FastAPI) -> FastAPI:
    auth = FastAPI()
    try:
        configure(auth)
    except Exception as e:
        logger.critical(f"Auth configuring is failed: {e}")
        sys.exit()
    logger.info("Auth created")
    app.mount(path="/auth", app=auth)
    return auth
