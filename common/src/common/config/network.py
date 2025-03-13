from pydantic_settings import BaseSettings
from pydantic import Field


class NetworkSettings(BaseSettings):
    host: str = Field(validation_alias="HOST", default="127.0.0.1")
    port: int = Field(validation_alias="PORT", default=5100)
    ssl_keyfile: str | None = Field(validation_alias="SSL_KEYFILE", default=None)
    ssl_certfile: str | None = Field(validation_alias="SSL_CERTFILE", default=None)

    root_path: str | None = Field(validation_alias="ROOT_PATH", default="")

    url: str = Field(validation_alias="URL")
