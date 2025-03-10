from abc import abstractmethod

from common.contracts.repository import BaseRepository
from app.schemas.file import FileCreateSchema, FileSchema


class FileRepository(BaseRepository):
    @abstractmethod
    async def create(self, file_create: FileCreateSchema) -> FileSchema:
        pass

    @abstractmethod
    async def update(self, id: int, file_update) -> FileSchema:
        pass

    @abstractmethod
    async def delete(self, id: int):
        pass

    @abstractmethod
    async def get_by_key(self, key: str) -> list[FileSchema]:
        pass

    @abstractmethod
    async def get_by_key_with_bucket(self, key: str, bucket: str) -> FileSchema | None:
        """Finds file by `FileSchema.key` and `FileSchema.bucket`.
        Returns:
            File if it exists, `None` otherwise.
        """
