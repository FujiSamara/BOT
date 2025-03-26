from common.schemas.base import BaseSchema


class DishSchema(BaseSchema):
    id: int
    name: str


class ProductSchema(BaseSchema):
    id: int
    name: str
    amount: float


class DishModifierSchema(BaseSchema):
    id: int
    products: list[ProductSchema]


class DishWithModifierSchema(DishSchema):
    modifiers: list[DishModifierSchema]
