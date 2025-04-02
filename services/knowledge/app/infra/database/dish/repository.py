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
from app.infra.database.knowledge.models import DishDivision, DishMaterial


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
                select(TTKDishModifier.id, TTKDishModifier.title)
                .where(TTKDishModifier.product_id == product_id)
                .subquery()
            )

            s = (
                select(
                    modifiers_s_sub.c.id,
                    modifiers_s_sub.c.title,
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
                    TTKProduct.title,
                    TTKAssemblyChart.ingredient_id,
                    TTKIngredient.title,
                    TTKAssemblyChart.amount,
                )
                .join(TTKIngredient, TTKIngredient.id == TTKAssemblyChart.ingredient_id)
                .join(TTKProduct, TTKProduct.id == TTKAssemblyChart.product_id)
                .where(TTKAssemblyChart.product_id == product_id)
            )

        rows = (await self._session.execute(s)).all()

        modifiers_dict: dict[int, dict] = {}
        for row in rows:
            modifier_id, modifier_title, ingredient_id, title, amount = row

            modifiers_dict.setdefault(
                modifier_id,
                {"id": modifier_id, "title": modifier_title, "ingredients": []},
            )["ingredients"].append(
                {
                    "id": ingredient_id,
                    "title": title,
                    "amount": amount,
                }
            )
        return [
            converters.modifier_to_modifier_schema(v) for v in modifiers_dict.values()
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

    async def get_dish_materials(self, product_id):
        s_materials = select(DishMaterial.external_id).where(
            DishMaterial.dish_id == product_id
        )
        s_video = select(TTKProduct.video).where(TTKProduct.id == product_id)

        materials = list((await self._session.execute(s_materials)).scalars().all())
        video = (await self._session.execute(s_video)).scalar_one_or_none()

        return converters.materials_to_materials_dto(materials, video)

    async def update(self, id, dish_update):
        s = select(TTKProduct).where(TTKProduct.id == id)
        product = (await self._session.execute(s)).scalars().first()

        if product is None:
            raise ValueError(f"Dish {id} not found.")

        for field, value in dish_update.model_dump(exclude_unset=True).items():
            setattr(product, field, value)

        await self._session.flush()
        await self._session.refresh(product)

        return converters.product_to_dish_schema(product)

    async def add_dish_materials(self, dish_id, materials):
        for material in materials:
            dm = DishMaterial(dish_id=dish_id, external_id=material)
            self._session.add(dm)

        await self._session.flush()
