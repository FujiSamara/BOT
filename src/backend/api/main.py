from fastapi import FastAPI
from api.configure import configure
import logging
import sys


def create(app: FastAPI) -> FastAPI:
    api = FastAPI(docs_url=None, redoc_url=None)
    try:
        configure(api)
    except Exception as e:
        logging.critical(f"Api configuring is failed: {e}")
        sys.exit()
    logging.info("Api created")
    app.mount(path="/api", app=api)
    return api
