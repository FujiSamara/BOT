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

    async def _get_dish_card_count_by_ids(self, division_ids: list[int]) -> list[int]:
        """Count dishes and cards count from first level of division for each id."""
        # Dishes count for every division
        dishes_count_s = (
            select(DishDivision.division_id, func.count(DishDivision.dish_id))
            .where(DishDivision.division_id.in_(division_ids))
            .group_by(DishDivision.division_id)
        )
        rows = (await self._session.execute(dishes_count_s)).all()
        dishes_count_dict = {row[0]: row[1] for row in rows}

        # Cards count for every division
        cards_count_s = (
            select(BusinessCard.division_id, func.count(BusinessCard.id))
            .where(BusinessCard.division_id.in_(division_ids))
            .group_by(BusinessCard.division_id)
        )
        rows = (await self._session.execute(cards_count_s)).all()
        cards_count_dict = {row[0]: row[1] for row in rows}

        return [
            dishes_count_dict.get(id, 0) + cards_count_dict.get(id, 0)
            for id in division_ids
        ]

    async def get_subdivisions_by_path(self, path):
        count = path.count("/")

        (level_filter,) = (
            func.length(Division.path)
            - func.length(func.replace(Division.path, "/", ""))
            == count + 1,
        )
        (sub_level_filter,) = (
            func.length(Division.path)
            - func.length(func.replace(Division.path, "/", ""))
            == count + 2,
        )

        replace_func = func.regexp_replace(Division.path, "/[^/]+$", "")
        sub_s = (
            select(
                replace_func.label("path"),
                func.count(replace_func).label("childs_count"),
            )
            .where(
                and_(
                    Division.path.startswith(path + "/"),
                    sub_level_filter,
                )
            )
            .group_by(replace_func)
        ).subquery()

        s = (
            select(Division, func.coalesce(sub_s.c.childs_count, 0))
            .where(
                and_(
                    Division.path.startswith(path + "/"),
                    level_filter,
                )
            )
            .outerjoin(sub_s, sub_s.c.path == Division.path)
        )

        rows = (await self._session.execute(s)).all()
        ids = [row[0].id for row in rows]
        counts = await self._get_dish_card_count_by_ids(ids)

        return [
            converters.division_to_subdivision_schema(
                row[0], subdivisions_count=row[1] + counts[i], files_count=0
            )
            for i, row in enumerate(rows)
        ]

    async def find_by_name(self, term):
        s = select(Division).where(Division.name.ilike(f"%{term}%"))
        divisions = (await self._session.execute(s)).scalars().all()
        d_ids = [d.id for d in divisions]

        # Dishes count for every division
        counts = await self._get_dish_card_count_by_ids(d_ids)

        for i, division in enumerate(divisions):
            count = division.path.count("/")
            (level_filter,) = (
                func.length(Division.path)
                - func.length(func.replace(Division.path, "/", ""))
                == count + 1,
            )
            childs_count_s = select(func.count(Division.id)).where(
                and_(
                    Division.path.startswith(division.path + "/"),
                    level_filter,
                )
            )
            subdivisions_count = (await self._session.execute(childs_count_s)).scalar()
            division.count = subdivisions_count + counts[i]

        return [
            converters.division_to_subdivision_schema(
                d, subdivisions_count=d.count, files_count=0
            )
            for d in divisions
        ]

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
