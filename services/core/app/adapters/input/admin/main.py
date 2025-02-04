from fastapi import FastAPI
import sys
from uuid import uuid4

from app.infra.logging import logger
from app.infra.config import settings
from app.infra.database.database import engine, session

from app.adapters.input.admin.admin import FujiAdmin, AdminAuth
from app.adapters.input.admin.configure import configure


def create(app: FastAPI) -> FastAPI:
    templates_dir = settings.app_directory_path + "/app/adapters/input/admin/templates"
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
