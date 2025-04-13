from typing import Self

from common.sql.uow import SQLUnitOfWork
from app.contracts.uow import DivisionUnitOfWork, CardUnitOfWork

from app.infra.database.dish.repository import SQLDishRepository
from app.infra.database.knowledge.repositories import (
    SQLCardRepository,
    SQLDivisionRepository,
)


class SQLCardUnitOfWork(SQLUnitOfWork, CardUnitOfWork):
    async def __aenter__(self) -> Self:
        uow = await super().__aenter__()
        self.card = SQLCardRepository(self._session)
        return uow


class SQLDivisionUnitOfWork(SQLCardUnitOfWork, DivisionUnitOfWork):
    async def __aenter__(self) -> Self:
        uow = await super().__aenter__()
        self.division = SQLDivisionRepository(self._session)
        self.dish = SQLDishRepository(self._session)
        return uow
