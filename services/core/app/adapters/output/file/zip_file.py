from zipfile import ZipFile
from os import path
from app.infra.config.settings import settings
from app.schemas import DocumentSchema
from io import BytesIO


class ZipFileManager:
    def __init__(self, files: list[DocumentSchema]):
        self.files: list[DocumentSchema] = files

    def create_zip(self) -> bytes:
        buffer = BytesIO()
        with ZipFile(buffer, mode="w") as zf:
            for file in self.files:
                if path.exists(
                    path.join(settings.storage_path, file.document.filename)
                ):
                    zf.write(path.join(settings.storage_path, file.document.filename))
        buffer.seek(0)
        return buffer.read()
