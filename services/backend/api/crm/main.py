from fastapi import FastAPI
from api.crm.configure import configure
import logging
import sys


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
