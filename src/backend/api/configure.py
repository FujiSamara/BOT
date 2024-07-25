from fastapi import FastAPI

from api import crm
from api import auth


def configure(api: FastAPI):
    """Configure fast api api app."""
    crm.create(api)
    auth.create(api)
