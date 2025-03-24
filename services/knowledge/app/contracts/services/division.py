from abc import abstractmethod

from common.contracts.services import BaseService

from app.schemas.division import DivisionOutSchema


class DivisionService(BaseService):
    @abstractmethod
    async def get_division_by_path(self, path: str) -> DivisionOutSchema | None:
        pass
