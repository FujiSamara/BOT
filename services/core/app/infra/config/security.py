from pydantic import Field, computed_field
from pydantic_settings import BaseSettings
from cryptography.hazmat.primitives import serialization


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

    access_token_expire_minutes: int = Field(
        validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES", default=30
    )
    token_algorithm: str = Field(validation_alias="TOKEN_ALGORITHM", default="RS256")

    public_key_path: str = Field(validation_alias="PUBLIC_KEY_PATH")
    private_key_path: str | None = Field(
        validation_alias="PRIVATE_KEY_PATH", default=None
    )

    @computed_field
    @property
    def public_key(self) -> str:
        with open(self.public_key_path, "r") as f:
            key = f.read()
            try:
                serialization.load_pem_public_key(key.encode())
            except Exception:
                raise ValueError("Provided non rsa public key.")
            return key

    @computed_field
    @property
    def private_key(self) -> str | None:
        if self.private_key_path is None:
            return None
        with open(self.private_key_path, "r") as f:
            key = f.read()
            try:
                serialization.load_pem_private_key(
                    key.encode(),
                    password=None,
                )
            except Exception:
                raise ValueError("Provided non rsa private key.")
            return key
