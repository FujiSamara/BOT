from abc import abstractmethod

from common.contracts.services import BaseService

from app.schemas.dish import DishSchema, DishModifierSchema, DishMaterialsSchema


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
