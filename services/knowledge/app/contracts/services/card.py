from abc import abstractmethod

from common.schemas.file import FileLinkSchema
from common.contracts.services import BaseService

from app.schemas.card import BusinessCardSchema


class CardService(BaseService):
    @abstractmethod
    async def get_card_by_id(self, id: int) -> BusinessCardSchema | None:
        pass

    @abstractmethod
    async def get_card_materials(self, card_id: int) -> list[FileLinkSchema]:
        pass
