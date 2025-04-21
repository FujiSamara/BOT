from common.schemas.base import BaseSchema


class BusinessCardSchema(BaseSchema):
    id: int

    name: str
    description: str | None
    materials_count: int


class BusinessCardUpdateSchema(BaseSchema):
    name: str | None = None
    description: str | None = None
