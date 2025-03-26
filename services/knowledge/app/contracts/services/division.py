from abc import abstractmethod

from common.contracts.services import BaseService

from app.schemas.division import DivisionOutSchema, DivisionSchema


class DivisionService(BaseService):
    @abstractmethod
    async def get_division_by_path(self, path: str) -> DivisionOutSchema | None:
        """Get division by path.
        - Note: Also finds cards and dishes as `DivisionSchema`.
        """

    @abstractmethod
    async def find_by_name(self, term: str) -> list[DivisionSchema]:
        """Find division by name.
        - Note: Also finds cards and dishes as `DivisionSchema`.
        - Note: Equivalent of `LIKE` statement.
        """
