from app.contracts.services import FileService
from app.contracts.clients import FileClient
from app.contracts.uow import FileUnitOfWork


class FileServiceImpl(FileService):
    def __init__(
        self, file_uow: FileUnitOfWork, file_client: FileClient, buckets: list[str]
    ):
        self._file_uow = file_uow
        self._file_client = file_client
        self._buckets = buckets

    async def create_put_link(self, file):
        return await self._file_client.create_put_link(self._buckets[0], file.key)

    async def create_get_link(self, key):
        return await self._file_client.create_get_link(self._buckets[0], key)

    async def confirm_putting(self, file_confirm):
        raise NotImplementedError
