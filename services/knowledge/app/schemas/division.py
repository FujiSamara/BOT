from enum import Enum
from common.schemas.base import BaseSchema


class DivisionType(Enum):
    division = "division"
    # Card types
    dish = "dish"
    business = "business"


class DivisionSchema(BaseSchema):
    id: int
    name: str
    path: str
    type: DivisionType = DivisionType.division


class SubdivisionSchema(DivisionSchema):
    subdivisions_count: int = 0
    files_count: int = 0


class DivisionOutSchema(DivisionSchema):
    subdivisions: list[SubdivisionSchema]
