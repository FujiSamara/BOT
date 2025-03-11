from datetime import datetime
from common.schemas import BaseSchemaPK, BaseSchema
from pydantic import ConfigDict, Field


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


class FileConfirmSchema(BaseSchema):
    key: str
    bucket: str
    size: int


class FileCreateSchema(BaseSchemaPK):
    name: str
    ext: str | None = None
    key: str
    bucket: str
    size: int
    created: datetime
    confirmed: bool


class FileSchema(FileCreateSchema):
    pass


class FileUpdateSchema(BaseSchema):
    name: str | None = None
    ext: str | None = None
    confirmed: bool | None = None
