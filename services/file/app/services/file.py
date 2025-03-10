from datetime import datetime
from app.contracts.services import FileService
from app.contracts.clients import FileClient
from app.contracts.uow import FileUnitOfWork
from app.schemas.file import FileCreateSchema


class FileServiceImpl(FileService):
    def __init__(
        self, file_uow: FileUnitOfWork, file_client: FileClient, buckets: list[str]
    ):
        self._file_uow = file_uow
        self._file_client = file_client
        self._buckets = buckets

    async def _find_free_bucket(self, key: str) -> str | None:
        """Finds first bucket not consists the file with `key`.
        Returns:
            Bucket name if it found, `None` otherwise.
        """
        async with self._file_uow as uow:
            files = await uow.file.get_by_key(key)

        for bucket in self._buckets:
            if not any([file.bucket == bucket for file in files]):
                return bucket

        return None

    async def create_put_link(self, file):
        bucket = await self._find_free_bucket(file.key)
        if bucket is None:
            raise KeyError(f"File {file.key} exists in each bucket.")

        async with self._file_uow as uow:
            raw = file.filename.split(".")
            name = raw[0]
            ext = None
            if len(raw) > 1:
                name = ".".join(raw[:-1])
                ext = raw[-1]

            file_create = FileCreateSchema(
                name=name,
                ext=ext,
                key=file.key,
                bucket=bucket,
                size=file.size,
                created=datetime.now(),
                confirmed=False,
            )
            await uow.file.create(file_create)

            return await self._file_client.create_put_link(bucket, file.key)

    async def create_get_link(self, id: int):
        async with self._file_uow as uow:
            file = await uow.file.get_by_id(id)
            if file is None:
                raise KeyError(f"File {id} not exists.")

        return await self._file_client.create_get_link(file.bucket, file.key)

    async def confirm_putting(self, file_confirm):
        raise NotImplementedError
