from app.contracts.services import CardService
from app.contracts.uow import CardUnitOfWork


class CardServiceImpl(CardService):
    def __init__(self, card_uow: CardUnitOfWork):
        self._uow = card_uow

    async def get_card_by_id(self, id):
        async with self._uow as uow:
            print(uow.card)
