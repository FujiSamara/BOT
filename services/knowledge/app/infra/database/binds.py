from sqlalchemy.ext.asyncio import AsyncEngine

from common.sql.orm import Base
from app.infra.database.knowledge import models as knowledge
from app.infra.database.dish import models as dish


def get_tables_binds(
    dish_engine: AsyncEngine, knowledge_engine: AsyncEngine
) -> dict[Base, AsyncEngine]:
    return {
        knowledge.BusinessCard: knowledge_engine,
        knowledge.BusinessCardMaterial: knowledge_engine,
        knowledge.Division: knowledge_engine,
        knowledge.DishDivision: knowledge_engine,
        knowledge.DishMaterial: knowledge_engine,
        dish.TTKProduct: dish_engine,
        dish.TTKDishModifier: dish_engine,
        dish.TTKProduct: dish_engine,
        dish.TTKGroup: dish_engine,
        dish.TTKIngredient: dish_engine,
    }
