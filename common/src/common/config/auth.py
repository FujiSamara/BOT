from pydantic_settings import BaseSettings
from pydantic import Field, computed_field
from cryptography.hazmat.primitives import serialization


class RemoteAuthSettings(BaseSettings):
    auth_url: str = Field(validation_alias="AUTH_URL")
    client_id: str = Field(validation_alias="CLIENT_ID")
    client_secret: str = Field(validation_alias="CLIENT_SECRET")
    with_auth_ssl: bool = Field(validation_alias="WITH_AUTH_SSL", default=True)


class LocalAuthSettings(BaseSettings):
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
