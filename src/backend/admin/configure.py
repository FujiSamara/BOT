from functools import lru_cache
from fastapi import FastAPI
import logging
from db.database import engine, session
from admin.shemas import RoleView

# Routers
from sqladmin import Admin

def configure(admin: FastAPI):
    '''Configure fast api admin app.
    '''
    admin_handler = Admin(
        admin, 
        engine, 
        session_maker=session,
        base_url='/', 
        title='Fuji admin',
    )
    admin_handler.add_view(RoleView)



@lru_cache
def get_admin_logger() -> logging.Logger:
    return logging.getLogger("admin")
