from abc import abstractmethod

from common.contracts.repository import BaseRepository
from app.schemas.dish import (
    DishSchema,
    DishMaterialsDTO,
    DishUpdateSchema,
    DishModifierGroupSchema,
)


class DishRepository(BaseRepository):
    @abstractmethod
    async def get_by_division_id(self, id: int) -> list[DishSchema]:
        pass

    @abstractmethod
    async def get_by_division_id_with_name(
        self, id: int, title: str
    ) -> DishSchema | None:
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> DishSchema | None:
        pass

    @abstractmethod
    async def get_modifiers(self, product_id: int) -> list[DishModifierGroupSchema]:
        pass

    @abstractmethod
    async def find_by_title(self, term: str) -> list[DishSchema]:
        pass

    @abstractmethod
    async def get_dish_materials(self, product_id: int) -> DishMaterialsDTO:
        pass

    @abstractmethod
    async def update(self, id: int, dish_update: DishUpdateSchema) -> DishSchema:
        pass

    @abstractmethod
    async def add_dish_materials(self, dish_id: int, materials: list[int]):
        """Add dish materials by `dish_id`.
        Returns:
            Added material ids.
        """

    @abstractmethod
    async def delete_dish_materials_by_external_id(self, id, material_ids: list[int]):
        """Delete dish materials by `material_ids`.
        Raises:
            ValueError: If dish with `id` not exist.
        """
