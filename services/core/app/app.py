from fastapi import FastAPI
from contextlib import asynccontextmanager

import app.admin
import app.bot
import app.api
from middlewares.setup import setup_core_middlewares


def create_app() -> FastAPI:
    app = FastAPI(lifespan=global_lifespan, docs_url=None, redoc_url=None)

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
