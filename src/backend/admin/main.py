from fastapi import FastAPI
from sqladmin import Admin
from admin.configure import configure, get_admin_logger
import sys
from db.database import engine, session


def create_admin(app: FastAPI) -> FastAPI:
    admin = Admin(
        app,
        engine=engine,
        session_maker=session,
        title='Fuji admin'
    )
    try:
        configure(admin)
    except Exception as e:
        get_admin_logger().critical(f"Admin configuring is failed: {e}")
        sys.exit()
    get_admin_logger().info("Admin created")
    return admin

