from abc import abstractmethod

from common.contracts.repository import BaseRepository
from app.schemas.division import DivisionSchema


class DivisionRepository(BaseRepository):
    @abstractmethod
    async def get_by_id(self, id: int) -> DivisionSchema | None:
        pass

    @abstractmethod
    async def get_by_path(self, path: str) -> DivisionSchema | None:
        pass

    @abstractmethod
    async def get_subdivisions_by_path(self, path: str) -> list[DivisionSchema]:
        """
        Returns:
            Subdivisions for `path`.
        """

    @abstractmethod
    async def find_by_name(self, term: str) -> list[DivisionSchema]:
        pass

    @abstractmethod
    async def get_division_paths_by_card(self, card_ids: list[int]) -> list[str]:
        pass

    @abstractmethod
    async def get_division_paths_by_dish(self, dish_ids: list[int]) -> list[str]:
        pass
