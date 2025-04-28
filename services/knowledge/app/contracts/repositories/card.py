from abc import abstractmethod

from common.contracts.repository import BaseRepository
from app.schemas.card import BusinessCardSchema, BusinessCardUpdateSchema


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

    @abstractmethod
    async def add_card_materials(self, card_id: int, materials: list[int]):
        pass

    @abstractmethod
    async def update(
        self, id: int, card_update: BusinessCardUpdateSchema
    ) -> BusinessCardSchema:
        """Update card in db by `id`.
        Raises:
            ValueError: If card with `id` not exist.
        Returns:
            Updated card.
        """

    @abstractmethod
    async def delete_card_materials_by_external_id(self, id, material_ids: list[int]):
        """Delete card materials by `material_ids`.
        Raises:
            ValueError: If card with `id` not exist.
        """
