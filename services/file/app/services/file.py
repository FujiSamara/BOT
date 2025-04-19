from datetime import datetime
from app.contracts.services import FileService
from app.contracts.clients import FileClient
from app.contracts.uow import FileUnitOfWork
from app.schemas.file import FileCreateSchema, FileUpdateSchema
from common.schemas.file import FileLinkSchema


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

    async def create_put_links(self, files, expiration=3600):
        file_create_list = []
        urls: list[str] = []
        result = []

        for file in files:
            bucket = await self._find_free_bucket(file.key)
            if bucket is None:
                continue

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
            file_create_list.append(file_create)

            url = await self._file_client.create_put_link(bucket, file.key, expiration)
            urls.append(url)

        async with self._file_uow as uow:
            schemas = await uow.file.create(file_create_list)

            for schema, url in zip(schemas, urls):
                name = schema.name
                if schema.ext is not None:
                    name += f".{schema.ext}"
                meta = FileLinkSchema(
                    id=schema.id,
                    url=url,
                    name=name,
                    size=schema.size,
                    created=schema.created,
                )
                result.append(meta)

        return result

    async def create_get_links(self, ids, expiration=3600):
        async with self._file_uow as uow:
            files = await uow.file.get_by_ids(ids)

            for file in files:
                if not file.confirmed:
                    await uow.file.delete(file.id)

        result = []

        for file in files:
            url = await self._file_client.create_get_link(
                file.bucket, file.key, expiration
            )
            name = file.name
            if file.ext is not None:
                name += f".{file.ext}"

            meta = FileLinkSchema(
                id=file.id,
                url=url,
                name=f"{file.name}.{file.ext}",
                size=file.size,
                created=file.created,
            )
            result.append(meta)

        return result

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
