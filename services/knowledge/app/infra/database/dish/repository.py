from sqlalchemy import select, and_


from common.sql.repository import SQLBaseRepository
from app.contracts.repositories import DishRepository
from app.infra.database.dish import converters
from app.infra.database.dish.models import (
    TTKDish,
    TTKDishModifier,
    TTKProduct,
    AssemblyChart,
)
from app.infra.database.knowledge.models import DishDivision


class SQLDishRepository(DishRepository, SQLBaseRepository):
    async def _get_dish_division_ids(self, id) -> list[int]:
        dish_divisions = select(DishDivision.dish_id).where(
            DishDivision.division_id == id
        )
        result = (await self._session.execute(dish_divisions)).scalars().all()
        return result

    async def get_by_division_id(self, id):
        dish_divisions = await self._get_dish_division_ids(id)
        s = select(TTKDish).where(TTKDish.id.in_(dish_divisions))

        dishes = (await self._session.execute(s)).scalars().all()
        return [converters.dish_to_dish_schema(d) for d in dishes]

    async def get_by_division_id_with_name(self, id, name):
        dish_divisions = await self._get_dish_division_ids(id)
        s = select(TTKDish).where(
            and_(TTKDish.id.in_(dish_divisions), TTKDish.name == name)
        )

        dish = (await self._session.execute(s)).scalars().first()
        return converters.dish_to_dish_schema(dish)

    async def get_modifiers(self, id):
        modifiers_s = (
            select(TTKDishModifier.id).where(TTKDishModifier.dish_id == id).subquery()
        )
        s = (
            select(
                modifiers_s.c.id,
                AssemblyChart.product_id,
                TTKProduct.name,
                AssemblyChart.amount,
            )
            .join(AssemblyChart, modifiers_s.c.id == AssemblyChart.modifier_id)
            .join(TTKProduct, TTKProduct.id == AssemblyChart.product_id)
        )

        rows = (await self._session.execute(s)).all()
        print(rows)
