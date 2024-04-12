from functools import lru_cache
import logging
from fastapi import FastAPI

# Apps
from admin.main import create_admin
from bot.main import create_bot

def configure(app: FastAPI):
    '''Configure fast api core app.
    '''
    create_admin(app)
    create_bot(app)
    

@lru_cache
def get_core_logger() -> logging.Logger:
    return logging.getLogger("core")