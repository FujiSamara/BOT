from common.schemas import BaseSchemaPK


class FileCreateSchema(BaseSchemaPK):
    name: str
    ext: str | None = None
    key: str
    bucket: str
    size: int


class FileSchema(FileCreateSchema):
    pass
