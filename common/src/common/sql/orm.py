from typing import TypeAlias, Type, Annotated, AsyncContextManager, Callable

from sqlalchemy import inspect
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, selectinload
from sqlalchemy.ext.asyncio import AsyncSession


intpk = Annotated[int, mapped_column(primary_key=True)]
GetSQLDB: TypeAlias = Callable[[], AsyncContextManager[AsyncSession]]


class Base(DeclarativeBase):
    id: Mapped[intpk]


def selectinload_all(model: Type[Base]):
    return [selectinload(relationship) for relationship in inspect(model).relationships]
