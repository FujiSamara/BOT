from fastapi import FastAPI
import logging

# Routers
from admin.routers.index import index

def configure(admin: FastAPI):
    '''Configure fast api admin app.
    '''
    admin.include_router(index, prefix='/index')
    logging.info(":Admin: /index mounted")