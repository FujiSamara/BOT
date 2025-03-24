from app.contracts.services import DivisionService
from app.contracts.uow import FullDivisionUnitOfWork

from app.schemas.division import DivisionSchema, DivisionType, DivisionOutSchema


class DivisionServiceImpl(DivisionService):
    def __init__(self, full_division_uow: FullDivisionUnitOfWork):
        self._uow = full_division_uow

    async def _try_find_division(self, path: str) -> DivisionSchema | None:
        async with self._uow as uow:
            division = await uow.division.get_by_path(path)
            if division is not None:
                return division

            parent_path = path[: path.rindex("/")]
            parent_division = await uow.division.get_by_path(parent_path)
            if parent_division is None:
                return

            card_business = await uow.card.get_by_division_id_with_name(
                parent_division.id, path.split("/")[-1]
            )
            if card_business is not None:
                return DivisionSchema(
                    id=card_business.id,
                    name=card_business.name,
                    path=path,
                    type=DivisionType.business,
                )

            dish = []  # TODO: Searching for dish

            return

    async def get_division_by_path(self, path):
        division = await self._try_find_division(path)
        if division is None:
            return division

        if division.type != DivisionType.division:
            return DivisionOutSchema(
                id=division.id,
                name=division.name,
                path=division.path,
                type=division.type,
                subdivisions=[],
            )

        async with self._uow as uow:
            subdivisions = await uow.division.get_subdivisions_by_path(division.path)

            business_cards = [
                DivisionSchema(
                    id=c.id,
                    path=division.path + "/" + c.name,
                    name=c.name,
                    type=DivisionType.business,
                )
                for c in await uow.card.get_by_division_id(division.id)
            ]
            subdivisions.extend(business_cards)

            result = DivisionOutSchema(
                id=division.id,
                name=division.name,
                path=division.path,
                type=division.type,
                subdivisions=subdivisions,
            )

        return result
