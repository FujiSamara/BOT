from fastapi import FastAPI

from api.auth.route import _register_general_routes


def configure(auth: FastAPI):
    """Configure fast api auth app."""
    _register_general_routes(auth)
