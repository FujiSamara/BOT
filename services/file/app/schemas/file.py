from datetime import datetime
from common.schemas import BaseSchemaPK, BaseSchema


class FileErrorSchema(BaseSchema):
    file_id: int
    message: str


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
    id: int


class FileUpdateSchema(BaseSchema):
    name: str | None = None
    ext: str | None = None
    confirmed: bool | None = None
