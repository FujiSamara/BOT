from fastapi import FastAPI
import sys
from uuid import uuid4

from app.admin.admin import FujiAdmin, AdminAuth
from app.admin.configure import configure
from app.infra.logging import logger
from app.infra.config import settings
from app.db.database import engine, session


def create(app: FastAPI) -> FastAPI:
    templates_dir = settings.app_directory_path + "/app/admin/templates"
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
        logger.critical(f"Admin configuring is failed: {e}")
        sys.exit()
    logger.info("Admin created")
    return admin
