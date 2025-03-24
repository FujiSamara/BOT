from sqlalchemy import select, ColumnElement, and_, func

from common.sql.repository import SQLBaseRepository

from app.infra.database.knowledge.models import Division
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
