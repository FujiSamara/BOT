from zipfile import ZipFile
from os import path
from app.infra.config.settings import settings
from app.schemas import DocumentSchema
from asyncio import get_running_loop
from io import BytesIO


class ZipFileManager:
    def __init__(self, files: list[DocumentSchema]):
        self.files: list[DocumentSchema] = files

    async def create_zip(self) -> bytes:
        loop = get_running_loop()
        future = loop.run_in_executor(None, self.__create_zip)
        return await future

    def __create_zip(self) -> bytes:
        buffer = BytesIO()
        with ZipFile(buffer, mode="w") as zf:
            for file in self.files:
                zf.write(path.join(settings.storage_path, file.document.filename))
        buffer.seek(0)
        return buffer.read()
