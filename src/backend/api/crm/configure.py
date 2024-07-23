from fastapi import FastAPI

from api.crm.routers import expenditure
from api.crm.routers import worker


def configure(crm: FastAPI):
    """Configure fast api crm app."""
    crm.include_router(expenditure.router, prefix="/expenditure")
    crm.include_router(worker.router, prefix="/worker")
