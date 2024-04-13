from functools import lru_cache
import logging
from fastapi import FastAPI

# Apps
import admin
import bot

def configure(app: FastAPI):
    '''Configure fast api core app.
    '''
    bot.create(app)
    admin.create(app)

@lru_cache
def get_core_logger() -> logging.Logger:
    return logging.getLogger("core")