from datetime import datetime
from pydantic import ConfigDict, Field

from common.schemas.base import BaseSchema, ErrorSchema


class FileInSchema(BaseSchema):
    filename: str = Field(description="Full filename")
    key: str = Field(description="Key for s3")
    size: int = Field(description="File size in bytes")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "filename": "test.txt",
                    "key": "test/test.txt",
                    "size": 2000,
                },
            ]
        },
    )


class FileMetaSchema(BaseSchema):
    id: int
    name: str
    size: int
    created: datetime


class FileLinkSchema(FileMetaSchema):
    url: str


class FileDeleteResultSchema(BaseSchema):
    file_id: int
    error: ErrorSchema | None
