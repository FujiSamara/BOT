from enum import Enum
from common.schemas.base import BaseSchema


class SubdivisionType(Enum):
    division = "division"
    # Card types
    dish = "dish"
    business = "business"


class SubdivisionSchema(BaseSchema):
    id: int
    name: str
    type: SubdivisionType


class DivisionSchema(BaseSchema):
    id: int
    name: str
    path: str


class DivisionOutSchema(DivisionSchema):
    subdivisions: list[SubdivisionSchema]
