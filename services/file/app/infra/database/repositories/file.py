from common.sql.repository import SQLBaseRepository
from app.contracts.repositories import FileRepository


class SQLFileRepository(FileRepository, SQLBaseRepository):
    async def create(self, file_create):
        raise NotImplementedError

    async def update(self, id, file_update):
        raise NotImplementedError

    async def delete(self, id):
        raise NotImplementedError

    async def get_by_key(self, key):
        raise NotImplementedError

    async def get_by_key_with_bucket(self, key, bucket):
        raise NotImplementedError
