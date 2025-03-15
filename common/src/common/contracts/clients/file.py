from abc import abstractmethod

from common.contracts.clients import BaseClient
from common.schemas.file import FileLinkSchema


class RemoteFileClient(BaseClient):
    @abstractmethod
    async def request_put_link(
        self, filename: str, key: str, size: int, expiration: int = 3600
    ) -> FileLinkSchema:
        pass

    @abstractmethod
    async def request_get_link(self, id: int, expiration: int = 3600) -> FileLinkSchema:
        pass
