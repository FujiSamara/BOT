from common.schemas.base import BaseSchema
from common.schemas.file import FileLinkSchema
from app.schemas.division import DivisionSchema


class BusinessCardSchema(BaseSchema):
    id: int

    name: str
    description: str | None

    division: DivisionSchema

    materials: list[int]


class BusinessCardOutSchema(BusinessCardSchema):
    materials: list[FileLinkSchema]
