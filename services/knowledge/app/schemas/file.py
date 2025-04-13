from common.schemas import BaseSchema
from pydantic import ConfigDict, Field


class FileInSchema(BaseSchema):
    filename: str = Field(description="Full filename")
    size: int = Field(description="File size in bytes")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "filename": "test.txt",
                    "size": 2000,
                },
            ]
        },
    )
