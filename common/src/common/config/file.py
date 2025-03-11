from pydantic_settings import BaseSettings
from pydantic import Field


class FileSettings(BaseSettings):
    file_url: str = Field(validation_alias="FILE_URL")
    with_file_ssl: bool = Field(validation_alias="WITH_FILE_SSL", default=True)
