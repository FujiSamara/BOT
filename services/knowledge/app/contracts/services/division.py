from abc import abstractmethod

from common.contracts.services import BaseService

from app.schemas.division import DivisionOutSchema


class DivisionService(BaseService):
    @abstractmethod
    async def get_division_by_id(self, id: int) -> DivisionOutSchema | None:
        pass
