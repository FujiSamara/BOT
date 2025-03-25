from abc import abstractmethod

from common.contracts.services import BaseService

from app.schemas.card import BusinessCardOutSchema


class CardService(BaseService):
    @abstractmethod
    async def get_card_by_id(self, id: int) -> BusinessCardOutSchema | None:
        pass
