from common.contracts.clients import RemoteFileClient
from app.contracts.services import CardService
from app.contracts.uow import CardUnitOfWork

from app.schemas.card import BusinessCardSchema


class CardServiceImpl(CardService):
    def __init__(self, card_uow: CardUnitOfWork, file_client: RemoteFileClient):
        self._uow = card_uow
        self._file_client = file_client

    async def get_card_by_id(self, id):
        async with self._uow as uow:
            card = await uow.card.get_by_id(id)
            if card is None:
                return None

            return BusinessCardSchema(
                id=card.id,
                name=card.name,
                description=card.description,
            )

    async def get_card_materials(self, card_id):
        async with self._uow as uow:
            materials = await uow.card.get_card_materials(card_id)

            return [await self._file_client.request_get_link(id) for id in materials]
