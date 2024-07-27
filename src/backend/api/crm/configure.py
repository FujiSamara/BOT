from fastapi import FastAPI

from api.crm.routers import expenditure
from api.crm.routers import worker
from api.crm.routers import budget
from api.crm.routers import department


def configure(crm: FastAPI):
    """Configure fast api crm app."""
    crm.include_router(expenditure.router, prefix="/expenditure")
    crm.include_router(worker.router, prefix="/worker")
    crm.include_router(budget.router, prefix="/budget")
    crm.include_router(department.router, prefix="/department")
