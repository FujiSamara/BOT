from common.schemas.base import BaseSchema
from app.schemas.division import DivisionSchema


class DishSchema(BaseSchema):
    id: int
    name: str
    division: DivisionSchema


class ProductSchema(BaseSchema):
    id: int
    name: str
    amount: float


class DishModifierSchema(BaseSchema):
    id: int
    products: list[ProductSchema]


class DishWithModifierSchema(DishSchema):
    modifiers: list[DishModifierSchema]
