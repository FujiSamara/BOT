from fastapi import FastAPI
from core.configure import configure

def create_app() -> FastAPI:
    app = FastAPI()
    configure(app)
    return app