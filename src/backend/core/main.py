from fastapi import FastAPI
from core.configure import configure, get_core_logger, global_lifespan
import sys

def create_app() -> FastAPI:
    app = FastAPI(lifespan=global_lifespan)
    try:
        configure(app)
    except Exception as e:
        get_core_logger().critical(f"Core configuring is failed: {e}")
        sys.exit()
    get_core_logger().info("Core created")
    return app