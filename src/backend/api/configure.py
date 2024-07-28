from fastapi import FastAPI

from api import crm
from api import auth

from api.route import register_base_routes


def configure(api: FastAPI):
    """Configure fast api api app."""
    register_base_routes(api)

    crm.create(api)
    auth.create(api)
