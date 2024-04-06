from fastapi import FastAPI
from admin.configure import configure
import logging

def create_admin() -> FastAPI:
    admin = FastAPI()
    try:
        configure(admin)
    except Exception as e:
        logging.critical(f"Admin configuring is failed: {e}")
        return admin
    logging.info("Admin created")
    return admin

