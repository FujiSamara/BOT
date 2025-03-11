from common.schemas.base import BaseSchema


class FileLinkSchema(BaseSchema):
    id: int
    url: str
