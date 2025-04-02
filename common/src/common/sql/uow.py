from typing import Self
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from common.contracts.uow import BaseUnitOfWork


class SQLUnitOfWork(BaseUnitOfWork):
    """
    Unit of work interface for SQLAlchemy, from which should be inherited all other units of work,
    which would be based on SQLAlchemy logics.
    """

    def __init__(self, session_factory: async_sessionmaker) -> None:
        super().__init__()
        self._session_factory: async_sessionmaker = session_factory

    async def __aenter__(self) -> Self:
        self._session_context = session_context = self._session_factory.begin()
        self._session: AsyncSession = await session_context.__aenter__()
        return await super().__aenter__()

    async def __aexit__(self, *args, **kwargs) -> None:
        await super().__aexit__(*args, **kwargs)
        await self._session_context.__aexit__(*args, **kwargs)
