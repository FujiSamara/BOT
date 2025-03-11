from common.schemas.base import BaseSchema


class ClientCredentials(BaseSchema):
    id: str
    scopes: list[str]
