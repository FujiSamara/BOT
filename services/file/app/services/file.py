from datetime import datetime
from app.contracts.services import FileService
from app.contracts.clients import FileClient
from app.contracts.uow import FileUnitOfWork
from app.schemas.file import FileCreateSchema, FileSchema, FileUpdateSchema
from common.schemas import ErrorSchema
from common.schemas.file import FileLinkSchema, FileDeleteResultSchema


class FileServiceImpl(FileService):
    def __init__(
        self, file_uow: FileUnitOfWork, file_client: FileClient, buckets: list[str]
    ):
        self._file_uow = file_uow
        self._file_client = file_client
        self._buckets = buckets

    async def _remove_unconfirmed(self, files: list[FileSchema]) -> list[FileSchema]:
        """Remove unconfirmed files in specidied `files`."""
        unconfirmed_files = [file for file in files if not file.confirmed]
        async with self._file_uow as uow:
            await uow.file.delete(unconfirmed_files)
        return [file for file in files if file.confirmed]

    async def _find_free_bucket(self, key: str) -> str | None:
        """Finds first bucket not consists the file with `key`.
        Returns:
            Bucket name if it found, `None` otherwise.
        """
        async with self._file_uow as uow:
            files = await uow.file.get_by_key(key)
        files = await self._remove_unconfirmed(files)

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
        files = await self._remove_unconfirmed(files)

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

    async def delete_files(self, ids):
        async with self._file_uow as uow:
            files = await uow.file.get_by_ids(ids)

            confirmed_file_kyes_buckets = [
                (file.key, file.bucket) for file in files if file.confirmed
            ]
            errors = await self._file_client.delete(confirmed_file_kyes_buckets)
            not_deleted_keys = set(error.key for error in errors)

            ids_to_delete = [
                file.id for file in files if file.key not in not_deleted_keys
            ]
            await uow.file.delete(ids_to_delete)

        key_id_dict = {file.key: file.id for file in files}
        id_error_msg_dict = {key_id_dict[error.key]: error.message for error in errors}

        found_ids = set(file.id for file in files)

        results = []

        for id in ids:
            if id not in found_ids:
                results.append(
                    FileDeleteResultSchema(
                        file_id=id, error=ErrorSchema(message="File not exist")
                    )
                )
            elif id in id_error_msg_dict:
                results.append(
                    FileDeleteResultSchema(
                        file_id=id, error=ErrorSchema(message=id_error_msg_dict[id])
                    )
                )
            else:
                results.append(FileDeleteResultSchema(file_id=id, error=None))

        return results
