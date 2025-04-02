import sys
import os
from functools import cache
from logging import Logger
from typing import Type, TypeVar
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

from common.config.postgres import PostgreSQLSettings
from common.config.network import NetworkSettings
from common.config.admin import AdminSettings
from common.config.auth import RemoteAuthSettings, LocalAuthSettings
from common.config.file import FileSettings

SettingsT = TypeVar("SettingsT", bound=BaseSettings)


@cache
def generate(SettingsClass: Type[SettingsT], logger: Logger) -> SettingsT:
    try:
        load_dotenv(override=True, dotenv_path=os.getcwd() + "/.env")
        return SettingsClass()
    except Exception as e:
        logger.critical(f"Settings generated with error: {e}")
        sys.exit(1)


__all__ = [
    "NetworkSettings",
    "PostgreSQLSettings",
    "AdminSettings",
    "RemoteAuthSettings",
    "LocalAuthSettings",
    "FileSettings",
]
