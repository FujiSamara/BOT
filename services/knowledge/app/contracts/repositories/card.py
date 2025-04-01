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

    @abstractmethod
    async def get_by_division_id_with_name(
        self, id: int, name: str
    ) -> BusinessCardSchema | None:
        pass

    @abstractmethod
    async def find_by_name(self, term: str) -> list[BusinessCardSchema]:
        pass

    @abstractmethod
    async def get_card_materials(self, card_id: int) -> list[int]:
        pass
