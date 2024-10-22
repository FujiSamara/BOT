from fastapi import FastAPI
import logging
import sys

from api.crm.routers import expenditure
from api.crm.routers import worker
from api.crm.routers import budget
from api.crm.routers import department
from api.crm.routers import bid
from api.crm.routers import worktime
from api.crm.routers import post


def create(api: FastAPI) -> FastAPI:
    crm = FastAPI()
    try:
        configure(crm)
    except Exception as e:
        logging.critical(f"Crm configuring is failed: {e}")
        sys.exit()
    logging.info("Crm created")
    api.mount(path="/crm", app=crm)
    return crm


def configure(crm: FastAPI):
    """Configure fast api crm app."""
    crm.include_router(expenditure.router, prefix="/expenditure")
    crm.include_router(worker.router, prefix="/worker")
    crm.include_router(budget.router, prefix="/budget")
    crm.include_router(department.router, prefix="/department")
    crm.include_router(bid.router, prefix="/bid")
    crm.include_router(worktime.router, prefix="/worktime")
    crm.include_router(post.router, prefix="/post")
