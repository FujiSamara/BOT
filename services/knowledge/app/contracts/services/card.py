from abc import abstractmethod

from common.schemas.file import FileLinkSchema
from common.contracts.services import BaseService

from app.schemas.card import BusinessCardSchema
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
