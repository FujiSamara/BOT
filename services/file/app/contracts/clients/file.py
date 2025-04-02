from abc import abstractmethod
from common.contracts.clients import BaseClient


class FileClient(BaseClient):
    @abstractmethod
    async def create_put_link(self, bucket: str, key: str, ttl: int = 3600):
        pass

    @abstractmethod
    async def create_get_link(self, bucket: str, key: str, ttl: int = 3600):
        pass
