from enum import Enum
from common.schemas.base import BaseSchema


class SubdivisionType(Enum):
    division = 1
    # Card types
    dish = 2
    business = 3


class SubdivisionSchema(BaseSchema):
    id: int
    name: int
    type: SubdivisionType


class DivisionSchema(BaseSchema):
    id: int
    name: str
    path: str


class DivisionOutSchema(DivisionSchema):
    subdivisions: list[SubdivisionSchema]
