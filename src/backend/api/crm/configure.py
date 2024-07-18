from fastapi import FastAPI

from api.crm.routers import panel


def configure(crm: FastAPI):
    """Configure fast api crm app."""
    crm.include_router(panel.router, prefix="/panel")
