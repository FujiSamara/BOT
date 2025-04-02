from app.schemas.file import FileCreateSchema, FileSchema
from app.infra.database.models import File


def file_create_schema_to_file(file_create: FileCreateSchema) -> File:
    return File(
        bucket=file_create.bucket,
        ext=file_create.ext,
        name=file_create.name,
        key=file_create.key,
        size=file_create.size,
        created=file_create.created,
        confirmed=file_create.confirmed,
    )


def file_to_file_schema(file: File) -> FileSchema:
    return FileSchema.model_validate(file)
