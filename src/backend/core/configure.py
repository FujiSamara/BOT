from functools import lru_cache
import logging
from fastapi import FastAPI
from db.orm import create_tables
import asyncio

# Apps
from admin.main import create_admin

def configure(app: FastAPI):
    '''Configure fast api core app.
    '''
    asyncio.run(create_tables())
    app.mount('/admin', create_admin())
    

@lru_cache
def get_core_logger() -> logging.Logger:
    return logging.getLogger("core")