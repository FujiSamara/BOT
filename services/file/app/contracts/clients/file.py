from abc import abstractmethod
from common.contracts.clients import BaseClient
from common.schemas.base import BaseSchema


class KeyErrorSchema(BaseSchema):
    key: str
    message: str


class FileClient(BaseClient):
    @abstractmethod
    async def create_put_link(self, bucket: str, key: str, ttl: int = 3600) -> str:
        pass

    @abstractmethod
    async def create_get_link(self, bucket: str, key: str, ttl: int = 3600) -> str:
        pass

    @abstractmethod
    async def delete(self, keys_buckets: list[tuple[str, str]]) -> list[KeyErrorSchema]:
        """Delete files in storage.

        Returns:
            A list of `KeyErrorSchema` objects describing the files that failed to be deleted.
        """
