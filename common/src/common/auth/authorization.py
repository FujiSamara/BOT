from datetime import datetime
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes

from common.contracts.services import AuthService
from common.schemas.client_credential import ClientCredentials


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

        if payload.expire < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return ClientCredentials.model_validate(payload)
