from common.schemas.base import BaseSchema
from common.schemas.file import FileLinkSchema


class BusinessCardSchema(BaseSchema):
    id: int

    name: str
    description: str | None

    materials: list[int]


class BusinessCardOutSchema(BusinessCardSchema):
    materials: list[FileLinkSchema]
