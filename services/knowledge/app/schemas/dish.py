from common.schemas.base import BaseSchema


class DishSchema(BaseSchema):
    id: int
    title: str
    image: str


class IngredientSchema(BaseSchema):
    id: int
    title: str
    amount: float


class DishModifierSchema(BaseSchema):
    id: int
    ingredients: list[IngredientSchema]


class DishWithModifierSchema(DishSchema):
    modifiers: list[DishModifierSchema]
