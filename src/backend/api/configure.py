from fastapi import FastAPI

from api import crm


def configure(api: FastAPI):
    """Configure fast api api app."""
    crm.create(api)
