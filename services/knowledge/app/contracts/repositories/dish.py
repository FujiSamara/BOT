from abc import abstractmethod

from common.contracts.repository import BaseRepository
from app.schemas.dish import DishSchema


class DishRepository(BaseRepository):
    @abstractmethod
    async def get_by_division_id(self, id: int) -> list[DishSchema]:
        pass

    @abstractmethod
    async def get_by_division_id_with_name(
        self, id: int, name: str
    ) -> DishSchema | None:
        pass
