from abc import abstractmethod

from common.contracts.services import BaseService
from common.schemas.file import FileInSchema
from app.schemas.file import FileConfirmSchema, FileDeleteResultSchema
from common.schemas.file import FileLinkSchema


class FileService(BaseService):
    @abstractmethod
    async def create_put_links(
        self, files: list[FileInSchema], expiration: int = 3600
    ) -> FileLinkSchema:
        """Create presigned urls for putting files.
        Create metadata for file with `confirmed=False`.
        Returns:
            Created links without files which `FileInSchema.key` already exists in all buckets.
        """

    @abstractmethod
    async def create_get_links(
        self, ids: list[int], expiration: int = 3600
    ) -> FileLinkSchema:
        """Create presigned urls for getting files.
        Returns:
            Created links without non existing files.
        """

    @abstractmethod
    async def confirm_putting(self, file_confirm: FileConfirmSchema):
        """Confirms putting file into s3 storage.
        Raises:
            KeyError: if file with specified `key` and `bucket` not exists.
            ValueError: if file validated with error.
        """

    @abstractmethod
    async def delete_files(self, ids: list[int]) -> list[FileDeleteResultSchema]:
        """Delete files meta from db and files from storage by `ids`.

        At first, tries to delete the files from the storage.
        Any file that fails to be deleted from the storage will not be removed from the database.

        Returns:
            A list of `FileDeleteResultSchema` objects describing the files that failed to be deleted.
        """
