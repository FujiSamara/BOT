from common.schemas.base import BaseSchema


class BusinessCardSchema(BaseSchema):
    id: int

    name: str
    description: str | None
