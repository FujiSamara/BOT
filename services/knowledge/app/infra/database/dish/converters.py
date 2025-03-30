from app.schemas.dish import DishSchema, DishModifierSchema
from app.infra.database.dish.models import TTKProduct


def product_to_dish_schema(dish: TTKProduct) -> DishSchema:
    return DishSchema.model_validate(dish)


def modifier_to_modifier_schema(modifier: dict) -> DishModifierSchema:
    return DishModifierSchema.model_validate(modifier)
