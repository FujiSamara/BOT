from datetime import timedelta
import jwt

from common.contracts.clients import SecurityClient
from common.schemas.token import TokenPayload
from common import now


class PyJWTSecurityClient(SecurityClient):
    algorithm = "RS256"

    def __init__(
        self,
        public_key: str,
        private_key: str | None,
        *,
        expires_delta: timedelta | None = None,
    ):
        self.expires_delta = expires_delta or timedelta(minutes=15)
        self._private_key = private_key
        self._public_key = public_key

    def create_access_token(self, data):
        if self._private_key is None:
            raise ValueError("Private key not specified for creating token.")
        expire = now() + self.expires_delta
        return jwt.encode(
            {"exp": expire, **data}, self._private_key, algorithm=self.algorithm
        )

    def parse_access_token(self, token):
        try:
            payload: dict = jwt.decode(
                token, self._public_key, algorithms=self.algorithm
            )
        except Exception:
            return
        client_id = payload.get("sub")
        expire = payload.get("exp")
        if client_id is None:
            return
        if expire is None:
            return
        scopes: str = payload.get("scopes", "")
        if isinstance(scopes, str):
            scopes = scopes.split()
        return TokenPayload(id=client_id, scopes=scopes, expire=expire)
