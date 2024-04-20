from fastapi import FastAPI
from admin.admin import FujiAdmin
from admin.configure import configure
import sys
from db.database import engine, session
import logging


def create(app: FastAPI) -> FastAPI:
    admin = FujiAdmin(
        app,
        engine=engine,
        session_maker=session,
        title='Fuji admin'
    )
    try:
        configure(admin)
    except Exception as e:
        logging.critical(f"Admin configuring is failed: {e}")
        sys.exit()
    logging.info("Admin created")
    return admin

