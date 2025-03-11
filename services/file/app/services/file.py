from datetime import datetime
from app.contracts.services import FileService
from common.contracts.clients import FileClient
from app.contracts.uow import FileUnitOfWork
from app.schemas.file import FileCreateSchema, FileUpdateSchema, LinkSchema


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

    async def create_put_link(self, file, expiration=3600):
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
            file = await uow.file.create(file_create)
            url = await self._file_client.create_put_link(bucket, file.key, expiration)

            return LinkSchema(id=file.id, url=url)

    async def create_get_link(self, id: int, expiration=3600):
        async with self._file_uow as uow:
            file = await uow.file.get_by_id(id)
            if file is None:
                raise KeyError(f"File {id} not exists.")

        url = await self._file_client.create_get_link(file.bucket, file.key, expiration)
        return LinkSchema(id=file.id, url=url)

    async def confirm_putting(self, file_confirm):
        async with self._file_uow as uow:
            file = await uow.file.get_by_key_with_bucket(
                file_confirm.key, file_confirm.bucket
            )
            if file is None:
                raise KeyError(f"File {file_confirm.key} not exists.")
            if file.size != file_confirm.size:
                raise ValueError(
                    f"Confirmed file size {file_confirm.size} "
                    f"doesn't equal exists {file.size}."
                )

            update = FileUpdateSchema(confirmed=True)
            await uow.file.update(file.id, update)
