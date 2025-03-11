from typing import Self

from common.sql.uow import SQLUnitOfWork
from app.contracts.uow import FileUnitOfWork

from app.infra.database.repositories import SQLFileRepository


class SQLFileUnitOfWork(SQLUnitOfWork, FileUnitOfWork):
    async def __aenter__(self) -> Self:
        uow = await super().__aenter__()
        self.file = SQLFileRepository(self._session)
        return uow
