from fastapi import FastAPI
from admin.configure import configure, get_admin_logger

def create_admin() -> FastAPI:
    admin = FastAPI()
    try:
        configure(admin)
    except Exception as e:
        get_admin_logger().critical(f"Admin configuring is failed: {e}")
        return admin
    get_admin_logger().info("Admin created")
    return admin

