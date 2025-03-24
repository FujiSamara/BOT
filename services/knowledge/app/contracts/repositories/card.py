from abc import abstractmethod

from common.contracts.repository import BaseRepository
from app.schemas.card import BusinessCardSchema


class CardRepository(BaseRepository):
    @abstractmethod
    async def get_by_id(self, id: int) -> BusinessCardSchema | None:
        pass

    @abstractmethod
    async def get_by_division_id(self, id: int) -> list[BusinessCardSchema]:
        pass
