from fastapi import FastAPI

from api.crm.routers import panel
from api.crm.routers import worker


def configure(crm: FastAPI):
    """Configure fast api crm app."""
    crm.include_router(panel.router, prefix="/panel")
    crm.include_router(worker.router, prefix="/worker")
