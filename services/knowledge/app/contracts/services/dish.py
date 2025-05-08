from abc import abstractmethod

from common.schemas.file import FileLinkSchema, FileDeleteResultSchema
from common.contracts.services import BaseService

from app.schemas.dish import DishSchema, DishModifierGroupSchema, DishMaterialsSchema
from app.schemas.file import FileInSchema


class DishService(BaseService):
    @abstractmethod
    async def get_dish_by_id(self, id: int) -> DishSchema | None:
        pass

    @abstractmethod
    async def get_dish_modifiers(self, dish_id: int) -> list[DishModifierGroupSchema]:
        pass

    @abstractmethod
    async def get_dish_materials(self, dish_id: int) -> DishMaterialsSchema:
        """Get metadata for dish materials.
        Raises:
            ValueError: If dish with `dish_id` not found.
        """

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

    @abstractmethod
    async def delete_dish_materials(
        self, dish_id: int, material_ids: list[int]
    ) -> list[FileDeleteResultSchema]:
        """Delete materials from dish.
        Raises:
            ValueError: If dish with `id` not exist.
        Returns:
            A list of `FileDeleteResultSchema` objects describing the materials that failed to be deleted.
        """

    @abstractmethod
    async def delete_dish_video(self, dish_id) -> FileDeleteResultSchema:
        """Delete video from dish if it exist.
        Raises:
            ValueError: If dish with `id` not exist.
            ValueError: If dish video not exist.
        Returns:
            A `FileDeleteResultSchema` object describing the video that failed to be deleted.
        """
