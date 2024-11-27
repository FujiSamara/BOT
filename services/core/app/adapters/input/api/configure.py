from fastapi import FastAPI

from app.api import crm
from app.api import auth
from app.api import external

from app.api.route import register_base_routes


def configure(api: FastAPI):
    """Configure fast api api app."""
    register_base_routes(api)

    crm.create(api)
    auth.create(api)
    external.create(api)
