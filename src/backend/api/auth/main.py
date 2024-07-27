from fastapi import FastAPI
from api.auth.configure import configure
import logging
import sys


def create(app: FastAPI) -> FastAPI:
    auth = FastAPI()
    try:
        configure(auth)
    except Exception as e:
        logging.critical(f"Auth configuring is failed: {e}")
        sys.exit()
    logging.info("Auth created")
    app.mount(path="/auth", app=auth)
    return auth
