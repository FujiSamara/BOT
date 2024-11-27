from fastapi import FastAPI
from app.admin.admin import FujiAdmin, AdminAuth
from app.admin.configure import configure
import sys
from app.db.database import engine, session
import logging
from settings import get_settings
from uuid import uuid4


def create(app: FastAPI) -> FastAPI:
    templates_dir = get_settings().app_directory_path + "/app/admin/templates"
    admin = FujiAdmin(
        app,
        engine=engine,
        session_maker=session,
        title="Fuji admin",
        templates_dir=templates_dir,
        authentication_backend=AdminAuth(secret_key=uuid4()),
    )
    try:
        configure(admin)
    except Exception as e:
        logging.critical(f"Admin configuring is failed: {e}")
        sys.exit()
    logging.info("Admin created")
    return admin
