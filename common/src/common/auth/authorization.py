import pytz
from datetime import datetime
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes

from common.contracts.services import AuthService
from common.schemas.client_credential import ClientCredentials
from common.schemas.token import TokenPayload


def expired(token: TokenPayload) -> bool:
    """Check token for expiration.
    Returns:
        `True` if token expired, `False` otherwise.
    """
    utc = pytz.UTC
    now = datetime.now().replace(tzinfo=utc)
    expire = token.expire.replace(tzinfo=utc)

    return expire < now


class Authorization:
    def __init__(self, auth_service: AuthService):
        self._auth_service = auth_service

    def _verify_scopes(self, scopes: list[str], *, needed_scopes: list[str]) -> bool:
        """Verifies that `scopes` enough for access with `needed_scopes`."""
        return "admin" in scopes or all(scope in scopes for scope in needed_scopes)

    async def __call__(
        self,
        scopes: SecurityScopes,
        credentials: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    ) -> ClientCredentials:
        """Checks `credentials` for `scopes`.

        Raises:
            HTTPException(status_code=status.HTTP_401_UNAUTHORIZED):
                If credential is invalid.

        Returns:
            Client credential with client **id** and client **scopes**
            if client authorization successful.
        """
        token = credentials.credentials
        scheme = credentials.scheme

        if scheme != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scheme of token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        payload = await self._auth_service.introspect(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not self._verify_scopes(payload.scopes, needed_scopes=scopes.scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough rights",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if expired(payload):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return ClientCredentials.model_validate(payload)
