from app.contracts.services import DivisionService
from app.contracts.uow import DivisionUnitOfWork

from app.schemas.division import DivisionSchema, DivisionType, DivisionOutSchema
from app.schemas.card import BusinessCardSchema
from app.schemas.dish import DishSchema


class DivisionServiceImpl(DivisionService):
    def __init__(self, full_division_uow: DivisionUnitOfWork):
        self._uow = full_division_uow

    def _business_card_to_division(self, card: BusinessCardSchema) -> DivisionSchema:
        return DivisionSchema(
            id=card.id,
            name=card.name,
            type=DivisionType.business,
            path=card.division.path + "/" + card.name,
        )

    def _dish_to_division(self, dish: DishSchema) -> DivisionSchema:
        return DivisionSchema(
            id=dish.id,
            name=dish.name,
            type=DivisionType.dish,
            path=dish.division.path + "/" + dish.name,
        )

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

            dish = await uow.dish.get_by_division_id_with_name(
                parent_division.id, path.split("/")[-1]
            )
            if dish is not None:
                return DivisionSchema(
                    id=dish.id, name=dish.name, path=path, type=DivisionType.dish
                )

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
                self._business_card_to_division(c)
                for c in await uow.card.get_by_division_id(division.id)
            ]
            subdivisions.extend(business_cards)

            dishes = [
                self._dish_to_division(d)
                for d in await uow.dish.get_by_division_id(division.id)
            ]
            subdivisions.extend(dishes)

            result = DivisionOutSchema(
                id=division.id,
                name=division.name,
                path=division.path,
                type=division.type,
                subdivisions=subdivisions,
            )

        return result

    async def find_by_name(self, term):
        async with self._uow as uow:
            divisions = await uow.division.find_by_name(term)
            cards = await uow.card.find_by_name(term)
            dishes = await uow.dish.find_by_name(term)

            divisions.extend([self._business_card_to_division(c) for c in cards])
            divisions.extend([self._dish_to_division(d) for d in dishes])

        return divisions
