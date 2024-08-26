from fastapi import FastAPI
from core.configure import configure, global_lifespan
import sys
import logging


def create_app() -> FastAPI:
    app = FastAPI(lifespan=global_lifespan, docs_url=None, redoc_url=None)
    try:
        configure(app)
    except Exception as e:
        logging.critical(f"Core configuring is failed: {e}")
        sys.exit()
    logging.info("Core created")
    return app
