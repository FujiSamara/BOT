import pathlib
from typing import Optional
from pydantic import Field, computed_field
import sys
from fastapi_storages import FileSystemStorage
from dotenv import load_dotenv

from app.infra.logging import logger
from app.infra.config.postgres import PostgreSQLSettings
from app.infra.config.bot import BotSettings
from app.infra.config.security import SecuritySettings


class Settings(PostgreSQLSettings, BotSettings, SecuritySettings):
    host: str = Field(validation_alias="HOST", default="127.0.0.1")
    domain: str = Field(validation_alias="DOMAIN", default="127.0.0.1")
    port: int = Field(validation_alias="PORT", default=5000)
    ssl_keyfile: Optional[str] = Field(validation_alias="SSL_KEYFILE", default=None)
    ssl_certfile: Optional[str] = Field(validation_alias="SSL_CERTFILE", default=None)
    external_api: str = Field(validation_alias="EXTERNAL_API")
    crm_addr: str = Field(validation_alias="CRM_ADDR")

    storage_path: str = Field(validation_alias="STORAGE_PATH", default="/tmp")
    stubname: str = Field(validation_alias="STUBNAME", default="stub.jpg")

    @computed_field
    @property
    def storage(self) -> FileSystemStorage:
        return FileSystemStorage(self.storage_path)

    @computed_field
    @property
    def app_directory_path(self) -> str:
        return (pathlib.Path(__file__).parent.parent.parent.parent).resolve().as_posix()

    date_format: str = "%d.%m.%Y"
    date_time_format: str = "%d.%m.%Y %H:%M:%S"
    time_format: str = "%H:%M:%S"


def _generate() -> Settings:
    """Generates settings of app."""
    load_dotenv(override=True)
    try:
        settings = Settings()
        return settings
    except Exception as e:
        logger.critical(f"Settings generated with error: {e}")
        sys.exit()


settings = _generate()
