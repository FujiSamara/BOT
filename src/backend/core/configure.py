from fastapi import FastAPI

# Apps
from admin.main import create_admin

def configure(app: FastAPI):
    '''Configure fast api core app.
    '''
    app.mount('/admin', create_admin())
    