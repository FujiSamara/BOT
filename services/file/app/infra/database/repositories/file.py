from sqlalchemy import select, ColumnElement, and_

from common.sql.repository import SQLBaseRepository
from app.contracts.repositories import FileRepository

from app.infra.database import converters
from app.infra.database.models import File


class SQLFileRepository(FileRepository, SQLBaseRepository):
    async def _get_by_criteria(self, element: ColumnElement) -> list[File]:
        s = select(File).filter(element)

        return (await self._session.execute(s)).scalars().all()

    async def create(self, file_creates):
        files = [
            converters.file_create_schema_to_file(file_create)
            for file_create in file_creates
        ]
        for file in files:
            self._session.add(file)

        await self._session.flush()
        for file in files:
            await self._session.refresh(file)

        return [converters.file_to_file_schema(file) for file in files]

    async def update(self, id, file_update):
        files = await self._get_by_criteria(File.id == id)
        if len(files) == 0:
            raise ValueError("File not exists")
        file = files[0]

        for field, value in file_update.model_dump(exclude_unset=True).items():
            setattr(file, field, value)

        await self._session.flush()
        await self._session.refresh(file)

        return converters.file_to_file_schema(file)

    async def delete(self, ids):
        files = await self._get_by_criteria(File.id.in_(ids))

        for file in files:
            await self._session.delete(file)

        await self._session.flush()

    async def get_by_key(self, key):
        files = await self._get_by_criteria(File.key == key)

        return [converters.file_to_file_schema(file) for file in files]

    async def get_by_id(self, id):
        files = await self._get_by_criteria(File.id == id)
        if len(files) == 0:
            return

        return converters.file_to_file_schema(files[0])

    async def get_by_key_with_bucket(self, key, bucket):
        files = await self._get_by_criteria(
            and_(File.key == key, File.bucket == bucket)
        )
        if len(files) == 0:
            return

        return converters.file_to_file_schema(files[0])

    async def get_by_ids(self, ids):
        files = await self._get_by_criteria(File.id.in_(ids))

        return [converters.file_to_file_schema(file) for file in files]
