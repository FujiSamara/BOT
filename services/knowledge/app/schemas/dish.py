from common.schemas.base import BaseSchema


class DishSchema(BaseSchema):
    id: int
    name: str


class ProductSchema(BaseSchema):
    name: str
    weight: float
    amount: float


class DishModifierSchema(BaseSchema):
    products: list[ProductSchema]


class DishWithModifierSchema(DishSchema):
    modifiers: list[DishModifierSchema]
