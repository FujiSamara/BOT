from fastapi import FastAPI
from core.configure import configure
import logging

def create_app() -> FastAPI:
    app = FastAPI()
    try:
        configure(app)
    except Exception as e:
        logging.critical(f"Core configuring is failed: {e}")
        return app
    logging.info("Core created")
    return app