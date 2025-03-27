from pydantic_settings import BaseSettings
from pydantic import Field, computed_field


class CORSSettings(BaseSettings):
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


class NetworkSettings(BaseSettings):
    host: str = Field(validation_alias="HOST", default="127.0.0.1")
    port: int = Field(validation_alias="PORT", default=5100)
    ssl_keyfile: str | None = Field(validation_alias="SSL_KEYFILE", default=None)
    ssl_certfile: str | None = Field(validation_alias="SSL_CERTFILE", default=None)

    root_path: str | None = Field(validation_alias="ROOT_PATH", default="")

    url: str = Field(validation_alias="URL")
