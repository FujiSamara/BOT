from abc import abstractmethod

from common.schemas.file import FileLinkSchema
from common.contracts.services import BaseService

from app.schemas.dish import DishSchema, DishModifierSchema, DishMaterialsSchema
from app.schemas.file import FileInSchema


class DishService(BaseService):
    @abstractmethod
    async def get_dish_by_id(self, id: int) -> DishSchema | None:
        pass

    @abstractmethod
    async def get_dish_modifiers(self, dish_id: int) -> list[DishModifierSchema]:
        pass

    @abstractmethod
    async def get_dish_materials(self, dish_id: int) -> DishMaterialsSchema:
        pass

    @abstractmethod
    async def add_dish_video(self, dish_id: int, video: FileInSchema) -> FileLinkSchema:
        """Create put link for dish video and registrated it in database.

        Raises:
            ValueError: If dish with `dish_id` not found.
        Returns:
            File put link with meta.
        """

    @abstractmethod
    async def add_dish_materials(
        self, dish_id: int, materials: list[FileInSchema]
    ) -> list[FileLinkSchema]:
        """Create put link for every dish material
        and registrated them in database.

        Raises:
            ValueError: If dish with `dish_id` not found or material already exist.
        Returns:
            File put links with meta.
        """
