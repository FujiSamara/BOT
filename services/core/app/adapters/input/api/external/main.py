from fastapi import FastAPI
import logging
import sys

from app.api.external.routers import equipment_status


def create(api: FastAPI) -> FastAPI:
    crm = FastAPI()
    try:
        configure(crm)
    except Exception as e:
        logging.critical(f"External subapp configuring is failed: {e}")
        sys.exit()
    logging.info("External subapp created")
    api.mount(path="/external", app=crm)
    return crm


def configure(external: FastAPI):
    """Configure fast api external subapp."""
    external.include_router(equipment_status.router, prefix="/equipment_status")
