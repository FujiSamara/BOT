from sqlalchemy import select, and_


from common.sql.repository import SQLBaseRepository
from app.contracts.repositories import DishRepository
from app.infra.database.dish import converters
from app.infra.database.dish.models import TTKDish
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
