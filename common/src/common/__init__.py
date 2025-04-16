from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from common.config import CORSSettings


def now() -> datetime:
    return datetime.now()


def with_cors(app: FastAPI, *, cors_settings: CORSSettings):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_settings.cors_origins,
        allow_credentials=True,
        allow_methods=cors_settings.cors_allow_methods,
        allow_headers=cors_settings.cors_allow_headers,
        expose_headers=cors_settings.expose_headers,
    )
