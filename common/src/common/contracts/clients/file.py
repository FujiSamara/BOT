from abc import abstractmethod

from common.contracts.clients import BaseClient
from common.schemas.file import FileLinkSchema, FileInSchema, FileDeleteResultSchema


class RemoteFileClient(BaseClient):
    @abstractmethod
    async def request_put_links(
        self, files: list[FileInSchema], expiration: int = 3600
    ) -> list[FileLinkSchema]:
        pass

    @abstractmethod
    async def request_get_links(
        self, ids: list[int], expiration: int = 3600
    ) -> list[FileLinkSchema]:
        pass

    @abstractmethod
    async def delete_files(self, ids: list[int]) -> list[FileDeleteResultSchema]:
        pass
