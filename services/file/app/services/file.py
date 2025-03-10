from app.contracts.services import FileService
from app.contracts.uow import FileUnitOfWork


class FileServiceImpl(FileService):
    def __init__(
        self,
        file_uow: FileUnitOfWork,
    ):
        self._file_uow = file_uow

    async def create_put_link(self, file):
        raise NotImplementedError

    async def create_get_link(self, key):
        raise NotImplementedError

    async def confirm_putting(self, file_confirm):
        raise NotImplementedError
