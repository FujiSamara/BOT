from fastapi import FastAPI

from app.adapters.input.api import crm
from app.adapters.input.api import auth
from app.adapters.input.api import external

from app.adapters.input.api.route import register_base_routes


def configure(api: FastAPI):
    """Configure fast api api app."""
    register_base_routes(api)

    crm.create(api)
    auth.create(api)
    external.create(api)
