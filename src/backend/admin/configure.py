from functools import lru_cache
from fastapi import FastAPI
import logging

# Routers
from admin.routers.index import index

def configure(admin: FastAPI):
    '''Configure fast api admin app.
    '''
    admin.include_router(index, prefix='/index')
    get_admin_logger().info("/index mounted")

@lru_cache
def get_admin_logger() -> logging.Logger:
    return logging.getLogger("admin")
