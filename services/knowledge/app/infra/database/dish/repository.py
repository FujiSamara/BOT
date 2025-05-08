from sqlalchemy import ColumnElement, select, and_, func


from common.sql.repository import SQLBaseRepository
from app.contracts.repositories import DishRepository
from app.infra.database.dish import converters
from app.infra.database.dish.models import (
    TTKProduct,
    TTKDishModifier,
    TTKAssemblyChart,
    TTKIngredient,
    TTKModifierGroup,
)
from app.infra.database.knowledge.models import DishDivision, DishMaterial
from app.schemas.dish import DishSchema


class SQLDishRepository(DishRepository, SQLBaseRepository):
    async def _get_by_criteria(self, element: ColumnElement) -> list[DishSchema]:
        s = select(TTKProduct).where(element)
        s_ids = select(TTKProduct.id).where(element)
        product_ids = (await self._session.execute(s_ids)).scalars().all()
        s_files = (
            select(DishMaterial.dish_id, func.coalesce(func.count(DishMaterial.id), 0))
            .group_by(DishMaterial.dish_id)
            .where(DishMaterial.dish_id.in_(product_ids))
        )

        dishes = (await self._session.execute(s)).scalars().all()
        dishes_id = (await self._session.execute(s_files)).all()
        dish_files_dict = {dish_id: files_count for dish_id, files_count in dishes_id}

        return [
            converters.product_to_dish_schema(
                dish, materials_count=dish_files_dict.get(dish.id, 0)
            )
            for dish in dishes
        ]

    async def _get_dish_division_ids(self, id) -> list[int]:
        dish_divisions = select(DishDivision.dish_id).where(
            DishDivision.division_id == id
        )
        result = (await self._session.execute(dish_divisions)).scalars().all()
        return list(result)

    async def get_by_division_id(self, id):
        dish_divisions = await self._get_dish_division_ids(id)
        return await self._get_by_criteria(TTKProduct.id.in_(dish_divisions))

    async def get_by_division_id_with_name(self, id, title):
        dish_divisions = await self._get_dish_division_ids(id)
        dishes = await self._get_by_criteria(
            and_(TTKProduct.id.in_(dish_divisions), TTKProduct.title == title)
        )

        if len(dishes) == 0:
            return

        return dishes[0]

    async def get_modifiers(self, product_id):
        s = (
            select(
                TTKAssemblyChart.product_id,
                TTKModifierGroup.title,
                TTKDishModifier.group_id,
                TTKDishModifier.title,
                TTKAssemblyChart.modifier_id,
                TTKAssemblyChart.ingredient_id,
                TTKIngredient.title,
                TTKAssemblyChart.amount,
            )
            .join(TTKIngredient, TTKIngredient.id == TTKAssemblyChart.ingredient_id)
            .join(TTKProduct, TTKProduct.id == TTKAssemblyChart.product_id)
            .join(
                TTKDishModifier,
                TTKDishModifier.id == TTKAssemblyChart.modifier_id,
                isouter=True,
            )
            .join(
                TTKModifierGroup,
                TTKModifierGroup.id == TTKDishModifier.group_id,
                isouter=True,
            )
            .where(TTKAssemblyChart.product_id == product_id)
        )

        rows = (await self._session.execute(s)).all()

        groups_dict: dict[int | None, dict] = {}

        for (
            product_id,
            group_title,
            group_id,
            modifier_title,
            modifier_id,
            ingredient_id,
            ingredient_title,
            amount,
        ) in rows:
            groups_dict.setdefault(group_id, {"title": group_title, "modifiers": {}})[
                "modifiers"
            ].setdefault(modifier_id, {"title": modifier_title, "ingredients": []})[
                "ingredients"
            ].append(
                {
                    "id": ingredient_id,
                    "title": ingredient_title,
                    "amount": amount,
                }
            )

        return [
            converters.modifier_group_to_modifier_group_schema(v)
            for v in groups_dict.values()
        ]

    async def get_by_id(self, id):
        dishes = await self._get_by_criteria(TTKProduct.id == id)
        if len(dishes) == 0:
            return

        return dishes[0]

    async def find_by_title(self, term):
        return await self._get_by_criteria(TTKProduct.title.ilike(f"%{term}%"))

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

    async def delete_dish_materials_by_external_id(self, id, material_ids):
        s = select(TTKProduct).where(TTKProduct.id == id)
        product = (await self._session.execute(s)).scalars().first()

        if product is None:
            raise ValueError(f"Dish {id} not found.")

        s_materials = select(DishMaterial).where(
            DishMaterial.external_id.in_(material_ids)
        )
        materials = list((await self._session.execute(s_materials)).scalars().all())

        for material in materials:
            await self._session.delete(material)

        await self._session.flush()
