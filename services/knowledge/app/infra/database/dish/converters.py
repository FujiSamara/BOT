from app.schemas.dish import DishSchema
from app.infra.database.dish.models import TTKDish


def dish_to_dish_schema(dish: TTKDish) -> DishSchema:
    return DishSchema.model_validate(dish)
