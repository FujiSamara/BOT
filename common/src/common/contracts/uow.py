from abc import ABC, abstractmethod
from typing import Self


class BaseUnitOfWork(ABC):
    """Interface for any units of work, which would be used for transaction atomicity, according DDD."""

    async def __aenter__(self) -> Self:
        return self

    @abstractmethod
    async def __aexit__(self, *args, **kwargs) -> None:
        pass
