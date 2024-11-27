from fastapi import FastAPI

from app.api.auth.route import register_general_routes


def configure(auth: FastAPI):
    """Configure fast api auth app."""
    register_general_routes(auth)
