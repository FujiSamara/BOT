from typing import Self

from common.sql.uow import SQLUnitOfWork
from app.contracts.uow import FullDivisionUnitOfWork

from app.infra.database.dish.repository import SQLDishRepository
from app.infra.database.knowledge.repositories import (
    SQLCardRepository,
    SQLDivisionRepository,
)


class SQLFullDivisionUnitOfWork(SQLUnitOfWork, FullDivisionUnitOfWork):
    async def __aenter__(self) -> Self:
        uow = await super().__aenter__()
        self.card = SQLCardRepository(self._session)
        self.division = SQLDivisionRepository(self._session)
        self.dish = SQLDishRepository(self._session)
        return uow
