from pydantic_settings import BaseSettings
from pydantic import Field, computed_field


class S3Settings(BaseSettings):
    region: str = Field(validation_alias="S3_REGION")
    endpoint_url: str = Field(validation_alias="S3_ENDPOINT_URL")
    buckets_str: str = Field(validation_alias="BUCKETS")
    access_key: str = Field(validation_alias="S3_ACCESS_KEY")
    secret_access_key: str = Field(validation_alias="S3_SECRET_ACCESS_KEY")

    @computed_field
    @property
    def buckets(self) -> list[str]:
        return self.buckets_str.split()
