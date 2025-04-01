from datetime import datetime
from common.schemas.base import BaseSchema


class FileMetaSchema(BaseSchema):
    id: int
    name: str
    size: float
    created: datetime


class FileLinkSchema(FileMetaSchema):
    url: str
