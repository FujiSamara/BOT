from pydantic import Field, computed_field
from pydantic_settings import BaseSettings
import uuid


class SecuritySettings(BaseSettings):
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
