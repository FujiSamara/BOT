from abc import abstractmethod

from common.contracts.services import BaseService
from app.schemas.file import FileInSchema, FileConfirmSchema
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
