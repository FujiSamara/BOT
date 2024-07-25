from fastapi import FastAPI

from api.auth.routers import index


def configure(auth: FastAPI):
    """Configure fast api auth app."""
    auth.include_router(index.router, prefix="/expenditure")
