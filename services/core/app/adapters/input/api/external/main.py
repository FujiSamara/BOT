from fastapi import FastAPI
import sys

from app.infra.logging import logger

from app.adapters.input.api.external.routers import equipment_status


def create(api: FastAPI) -> FastAPI:
    crm = FastAPI()
    try:
        configure(crm)
    except Exception as e:
        logger.critical(f"External subapp configuring is failed: {e}")
        sys.exit()
    logger.info("External subapp created")
    api.mount(path="/external", app=crm)
    return crm


def configure(external: FastAPI):
    """Configure fast api external subapp."""
    external.include_router(equipment_status.router, prefix="/equipment_status")
