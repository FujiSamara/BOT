from abc import abstractmethod

from common.schemas.file import FileLinkSchema, FileDeleteResultSchema
from common.contracts.services import BaseService

from app.schemas.card import BusinessCardSchema, BusinessCardUpdateSchema
from app.schemas.file import FileInSchema


class CardService(BaseService):
    @abstractmethod
    async def get_card_by_id(self, id: int) -> BusinessCardSchema | None:
        pass

    @abstractmethod
    async def get_card_materials(self, card_id: int) -> list[FileLinkSchema]:
        pass

    @abstractmethod
    async def add_card_materials(
        self, card_id: int, materials: list[FileInSchema]
    ) -> list[FileLinkSchema]:
        """Create put link for every card material
        and registrated them in database.

        Raises:
            ValueError: If dish with `card_id` not found or material already exist.
        Returns:
            File put links with meta.
        """

    @abstractmethod
    async def update_card(
        self, card_id: int, card_update: BusinessCardUpdateSchema
    ) -> BusinessCardSchema:
        """Update card by `card_id`
        Raises:
            ValueError: If card with `id` not exist.
        Returns:
            Updated card.
        """

    @abstractmethod
    async def deleta_card_materials(
        self, card_id: int, material_ids: list[int]
    ) -> list[FileDeleteResultSchema]:
        """Delete materials from card.
        Raises:
            ValueError: If card with `id` not exist.
        Returns:
            A list of `FileDeleteResultSchema` objects describing the materials that failed to be deleted.
        """
