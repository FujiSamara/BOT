from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, computed_field
from functools import lru_cache
import logging
import sys
from fastapi_storages import FileSystemStorage

class Settings(BaseSettings):
    # main
    host: str = Field(validation_alias="HOST", default="127.0.0.1")
    port: int = Field(validation_alias="PORT", default=5000)
    ssl_keyfile: Optional[str] = Field(validation_alias="SSL_KEYFILE", default=None)
    ssl_certfile: Optional[str] = Field(validation_alias="SSL_CERTFILE", default=None)
    storage_path: str = Field(validation_alias="STORAGE_PATH", default="/tmp")

    @computed_field
    @property
    def storage(self) -> FileSystemStorage:
        return FileSystemStorage(self.storage_path) 

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
            f"postgresql+psycopg://{self.psql_user}:{self.psql_pass}" + 
            f"@{self.psql_host}:{self.psql_port}/{self.psql_db_name}"
        )
    
    # bot
    bot_token: str = Field(validate_default="BOT_TOKEN")
    telegram_token: str = Field(validate_default="TELEGRAM_TOKEN")
    bot_webhook_url: str = Field(validate_default="BOT_WEBHOOK_URL")

@lru_cache
def get_settings() -> Settings:
    '''Returns settings of app.

    Settings will be generate only for first call.
    '''
    try:
        settings = Settings()
        return settings
    except Exception as e:
        logging.critical(f"Settings generated with error: {e}")
        sys.exit()