from datetime import datetime
from common.schemas.client_credential import ClientCredentials
from common.schemas.base import BaseSchema


class TokenPayload(ClientCredentials):
    expire: datetime


class TokenPayloadShort(BaseSchema):
    expire: datetime
    token: str
