from abc import abstractmethod

from common.contracts.repository import BaseRepository
from app.schemas.dish import DishSchema, DishModifierSchema


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
    async def get_modifiers(self, product_id: int) -> list[DishModifierSchema]:
        pass

    @abstractmethod
    async def find_by_title(self, term: str) -> list[DishSchema]:
        pass
