from app.contracts.services import DivisionService
from app.contracts.uow import FullDivisionUnitOfWork

from app.schemas.division import SubdivisionSchema, SubdivisionType, DivisionOutSchema


class DivisionServiceImpl(DivisionService):
    def __init__(self, full_division_uow: FullDivisionUnitOfWork):
        self._uow = full_division_uow

    async def get_division_by_path(self, path):
        async with self._uow as uow:
            division = await uow.division.get_by_path(path)
            if division is None:
                raise ValueError("Division not exist")

            subdivisions = [
                SubdivisionSchema(id=d.id, name=d.name, type=SubdivisionType.division)
                for d in await uow.division.get_subdivisions_by_path(division.path)
            ]

            cards = [
                SubdivisionSchema(id=c.id, name=c.name, type=SubdivisionType.business)
                for c in await uow.card.get_by_division_id(division.id)
            ]
            subdivisions.extend(cards)

            result = DivisionOutSchema(
                id=division.id,
                name=division.name,
                path=division.path,
                subdivisions=subdivisions,
            )

        return result
