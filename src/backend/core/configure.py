from fastapi import FastAPI
from contextlib import asynccontextmanager

# Apps
import admin
import bot

def configure(app: FastAPI):
    '''Configure fast api core app.
    '''
    bot.create(app)
    admin.create(app)

@asynccontextmanager
async def global_lifespan(app: FastAPI):
    bot_l = bot.lifespan(app)
    await anext(bot_l)
    yield
    await anext(bot_l)