from datetime import datetime
from common.schemas import BaseSchemaPK, BaseSchema


class FileInSchema(BaseSchema):
    filename: str
    key: str
    size: int


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
    confirmed: str | None = None
