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


class DivisionOutSchema(DivisionSchema):
    subdivisions: list[DivisionSchema]
