from abc import abstractmethod

from common.contracts.repository import BaseRepository
from app.schemas.file import FileCreateSchema, FileSchema, FileUpdateSchema


class FileRepository(BaseRepository):
    @abstractmethod
    async def create(self, file_creates: list[FileCreateSchema]) -> list[FileSchema]:
        pass

    @abstractmethod
    async def update(self, id: int, file_update: FileUpdateSchema) -> FileSchema:
        pass

    @abstractmethod
    async def delete(self, id: int):
        pass

    @abstractmethod
    async def get_by_key(self, key: str) -> list[FileSchema]:
        pass

    @abstractmethod
    async def get_by_id(self, id: int) -> FileSchema | None:
        pass

    @abstractmethod
    async def get_by_ids(self, ids: list[int]) -> list[FileSchema]:
        pass

    @abstractmethod
    async def get_by_key_with_bucket(self, key: str, bucket: str) -> FileSchema | None:
        pass
