from pydantic_settings import BaseSettings
from pydantic import Field, computed_field
from functools import lru_cache
import logging
import sys

class Settings(BaseSettings):
    # psql 
    psql_pass: str = Field(validation_alias="POSTGRES_PASSWORD")
    psql_user: str = Field(validation_alias="POSTGRES_USER")
    psql_host: str = Field(validation_alias="POSTGRES_HOST", default="localhost")
    psql_port: int = Field(validation_alias="POSTGRES_HOST", default=5432)
    psql_db_name: str = Field(validation_alias="POSTGRES_DB_NAME", default="db")

    @computed_field
    @property
    def psql_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.psql_user}:{self.psql_pass}" + 
            f"@{self.psql_host}:{self.psql_port}/{self.psql_db_name}"
        )
    



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