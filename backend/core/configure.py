from fastapi import FastAPI
from contextlib import asynccontextmanager

from core.middlewares.setup import setup_core_middlewares

# Apps
import admin
import bot
import api


def configure(app: FastAPI):
    """Configures fast api core app."""
    bot.create(app)
    admin.create(app)
    api.create(app)

    setup_core_middlewares(app)


@asynccontextmanager
async def global_lifespan(app: FastAPI):
    lifespans = []

    lifespans.append(bot.lifespan(app))

    for lifespan in lifespans:
        await anext(lifespan)
    yield
    for lifespan in lifespans:
        await anext(lifespan)
