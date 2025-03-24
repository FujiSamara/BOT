from app.contracts.services import DivisionService
from app.contracts.uow import FullDivisionUnitOfWork


class DivisionServiceImpl(DivisionService):
    def __init__(self, full_division_uow: FullDivisionUnitOfWork):
        self._uow = full_division_uow

    async def get_division_by_id(self, id):
        async with self._uow as uow:
            print(uow.division)
