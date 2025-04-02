from abc import abstractmethod

from common.contracts.services import BaseService
from app.schemas.file import FileInSchema, FileConfirmSchema
from common.schemas.file import FileLinkSchema


class FileService(BaseService):
    @abstractmethod
    async def create_put_link(
        self, file: FileInSchema, expiration: int = 3600
    ) -> FileLinkSchema:
        """Create presigned url for putting file.
        Create metadata for file with `confirmed=False`.
        Raises:
            KeyError: if file with specified `FileInSchema.key` already exists in all buckets.
        Returns:
            Created link.
        """

    @abstractmethod
    async def create_get_link(self, id: int, expiration: int = 3600) -> FileLinkSchema:
        """Create presigned url for getting file.
        Raises:
            KeyError: if file with specified `id` not exists.
        Returns:
            Created link.
        """

    @abstractmethod
    async def confirm_putting(self, file_confirm: FileConfirmSchema):
        """Confirms putting file into s3 storage.
        Raises:
            KeyError: if file with specified `key` and `bucket` not exists.
            ValueError: if file validated with error.
        """
