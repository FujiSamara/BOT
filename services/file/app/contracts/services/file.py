from abc import abstractmethod

from common.contracts.services import BaseService
from app.schemas.file import FileInSchema, FileConfirmSchema


class FileService(BaseService):
    @abstractmethod
    async def create_put_link(self, file: FileInSchema) -> str:
        """Create presigned url for putting file.
        Create metadata for file with `confirmed=False`.
        Raises:
            KeyError: if file with specified `FileInSchema.key` already exists in all buckets.
        Returns:
            Created link.
        """

    @abstractmethod
    async def create_get_link(self, id: int) -> str:
        """Create presigned url for getting file.
        Raises:
            KeyError: if file with specified `id` not exists.
        Returns:
            Created link.
        """

    @abstractmethod
    async def confirm_putting(self, file_confirm: FileConfirmSchema):
        """Confirms putting file into s3 storage."""
