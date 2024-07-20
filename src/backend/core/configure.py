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
    bot_l = bot.lifespan(app)
    await anext(bot_l)
    yield
    await anext(bot_l)
