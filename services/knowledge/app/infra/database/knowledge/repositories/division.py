from sqlalchemy import select, ColumnElement, and_, func

from common.sql.repository import SQLBaseRepository

from app.infra.database.knowledge.models import Division, BusinessCard, DishDivision
from app.infra.database.knowledge import converters
from app.contracts.repositories import DivisionRepository


class SQLDivisionRepository(DivisionRepository, SQLBaseRepository):
    async def _get_by(self, column: ColumnElement, value) -> Division | None:
        s = select(Division).where(column == value)

        return (await self._session.execute(s)).scalars().first()

    async def get_by_id(self, id):
        division = await self._get_by(Division.id, id)
        if division is None:
            return None

        return converters.division_to_division_schema(division)

    async def get_by_path(self, path):
        division = await self._get_by(Division.path, path)
        if division is None:
            return None

        return converters.division_to_division_schema(division)

    async def get_subdivisions_by_path(self, path):
        count = path.count("/")

        (level_filter,) = (
            func.length(Division.path)
            - func.length(func.replace(Division.path, "/", ""))
            == count + 1,
        )

        s = select(Division).where(
            and_(
                Division.path.startswith(path + "/"),
                level_filter,
            )
        )

        subdivisions = (await self._session.execute(s)).scalars().all()

        return [converters.division_to_division_schema(d) for d in subdivisions]

    async def find_by_name(self, term):
        s = select(Division).where(Division.name.ilike(f"%{term}%"))
        divisions = (await self._session.execute(s)).scalars().all()

        return [converters.division_to_division_schema(d) for d in divisions]

    async def get_division_paths_by_card(self, card_ids):
        s = (
            select(BusinessCard.id, Division.path)
            .join(BusinessCard, BusinessCard.division_id == Division.id)
            .where(BusinessCard.id.in_(card_ids))
        )

        rows = (await self._session.execute(s)).all()
        card_id_dict = {}
        for card_id, path in rows:
            card_id_dict[card_id] = path

        return [card_id_dict[id] for id in card_ids]

    async def get_division_paths_by_dish(self, dish_ids):
        s = (
            select(DishDivision.dish_id, Division.path)
            .join(Division, Division.id == DishDivision.division_id)
            .where(DishDivision.dish_id.in_(dish_ids))
        )

        rows = (await self._session.execute(s)).all()
        dish_id_dict = {}
        for dish_id, path in rows:
            dish_id_dict[dish_id] = path

        return [dish_id_dict[id] for id in dish_ids]
