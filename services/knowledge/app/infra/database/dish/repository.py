from sqlalchemy import select, and_, func


from common.sql.repository import SQLBaseRepository
from app.contracts.repositories import DishRepository
from app.infra.database.dish import converters
from app.infra.database.dish.models import (
    TTKProduct,
    TTKDishModifier,
    TTKAssemblyChart,
    TTKIngredient,
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
        s = select(TTKProduct).where(TTKProduct.id.in_(dish_divisions))

        dishes = (await self._session.execute(s)).scalars().all()
        return [converters.product_to_dish_schema(d) for d in dishes]

    async def get_by_division_id_with_name(self, id, title):
        dish_divisions = await self._get_dish_division_ids(id)
        s = select(TTKProduct).where(
            and_(TTKProduct.id.in_(dish_divisions), TTKProduct.title == title)
        )

        dish = (await self._session.execute(s)).scalars().first()
        if dish is None:
            return None

        return converters.product_to_dish_schema(dish)

    async def get_modifiers(self, product_id):
        modifiers_count = (
            await self._session.execute(
                select(func.count(TTKDishModifier.id)).where(
                    TTKDishModifier.product_id == product_id
                )
            )
        ).scalar_one()

        if modifiers_count != 0:
            modifiers_s_sub = (
                select(TTKDishModifier.id)
                .where(TTKDishModifier.product_id == product_id)
                .subquery()
            )

            s = (
                select(
                    modifiers_s_sub.c.id,
                    TTKAssemblyChart.ingredient_id,
                    TTKIngredient.title,
                    TTKAssemblyChart.amount,
                )
                .join(
                    TTKAssemblyChart,
                    modifiers_s_sub.c.id == TTKAssemblyChart.modifier_id,
                )
                .join(TTKIngredient, TTKIngredient.id == TTKAssemblyChart.ingredient_id)
            )
        else:
            s = (
                select(
                    TTKAssemblyChart.product_id,
                    TTKAssemblyChart.ingredient_id,
                    TTKIngredient.title,
                    TTKAssemblyChart.amount,
                )
                .join(TTKIngredient, TTKIngredient.id == TTKAssemblyChart.ingredient_id)
                .where(TTKAssemblyChart.product_id == product_id)
            )

        rows = (await self._session.execute(s)).all()

        modifiers_dict: dict[int, list] = {}
        for row in rows:
            modifier_id, ingredient_id, title, amount = row

            modifiers_dict.setdefault(modifier_id, []).append(
                {
                    "id": ingredient_id,
                    "title": title,
                    "amount": amount,
                }
            )
        return [
            converters.modifier_to_modifier_schema({"id": k, "ingredients": v})
            for k, v in modifiers_dict.items()
        ]

    async def get_by_id(self, id):
        s = select(TTKProduct).where(TTKProduct.id == id)

        dish = (await self._session.execute(s)).scalars().first()
        if dish is None:
            return None

        return converters.product_to_dish_schema(dish)

    async def find_by_title(self, term):
        s = select(TTKProduct).where(TTKProduct.title.ilike(f"%{term}%"))
        dishes = (await self._session.execute(s)).scalars().all()

        return [converters.product_to_dish_schema(d) for d in dishes]
