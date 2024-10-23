import pathlib
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, computed_field
from functools import lru_cache
import logging
import sys
from fastapi_storages import FileSystemStorage
from dotenv import load_dotenv
import uuid


class Settings(BaseSettings):
    # region Network
    host: str = Field(validation_alias="HOST", default="127.0.0.1")
    domain: str = Field(validation_alias="DOMAIN", default="127.0.0.1")
    port: int = Field(validation_alias="PORT", default=5000)
    ssl_keyfile: Optional[str] = Field(validation_alias="SSL_KEYFILE", default=None)
    ssl_certfile: Optional[str] = Field(validation_alias="SSL_CERTFILE", default=None)
    external_api: str = Field(validation_alias="EXTERNAL_API")
    crm_addr: str = Field(validation_alias="CRM_ADDR")
    # endregion

    # region Security
    cors_origins_str: str = Field(
        validation_alias="CORS_ORIGINS", default="http://localhost:5001"
    )

    @computed_field
    @property
    def cors_origins(self) -> list[str]:
        return self.cors_origins_str.split()

    cors_allow_methods: list[str] = ["GET", "POST", "PATCH", "PUT", "DELETE"]
    cors_allow_headers: list[str] = [
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ]
    expose_headers: list[str] = ["Content-Disposition"]

    secret_key: str = Field(validation_alias="SECRET_KEY", default=str(uuid.uuid4()))
    access_token_expire_minutes: int = Field(
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES", default=30
    )
    token_algorithm: str = Field(validation_alias="TOKEN_ALGORITHM", default="HS256")
    # endregion

    # region Storages
    storage_path: str = Field(validation_alias="STORAGE_PATH", default="/tmp")

    @computed_field
    @property
    def storage(self) -> FileSystemStorage:
        return FileSystemStorage(self.storage_path)

    @computed_field
    @property
    def app_directory_path(self) -> str:
        return (pathlib.Path(__file__).parent).resolve().as_posix()

    # psql
    psql_pass: str = Field(validation_alias="POSTGRES_PASSWORD")
    psql_user: str = Field(validation_alias="POSTGRES_USER")
    psql_host: str = Field(validation_alias="POSTGRES_HOST", default="127.0.0.1")
    psql_port: int = Field(validation_alias="POSTGRES_PORT", default=5432)
    psql_db_name: str = Field(validation_alias="POSTGRES_DB_NAME", default="postgres")

    @computed_field
    @property
    def psql_dsn(self) -> str:
        return (
            f"postgresql+psycopg://{self.psql_user}:{self.psql_pass}"
            + f"@{self.psql_host}:{self.psql_port}/{self.psql_db_name}"
        )

    # endregion

    # bot
    bot_token: str = Field(validate_default="BOT_TOKEN")
    telegram_token: str = Field(validate_default="TELEGRAM_TOKEN")
    bot_webhook_url: str = Field(validate_default="BOT_WEBHOOK_URL")

    date_format: str = "%d.%m.%Y"
    date_time_format: str = "%d.%m.%Y %H:%M:%S"


@lru_cache
def get_settings() -> Settings:
    """Returns settings of app.

    Settings will be generate only for first call.
    """
    load_dotenv(override=True)
    try:
        settings = Settings()
        return settings
    except Exception as e:
        logging.critical(f"Settings generated with error: {e}")
        sys.exit()


logger = logging.getLogger("uvicorn.error")
