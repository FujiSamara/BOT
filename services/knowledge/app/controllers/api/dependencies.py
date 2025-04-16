from fastapi import Depends
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes
from dependency_injector.wiring import Provide, inject

from common import auth
from common.schemas.client_credential import ClientCredentials
from app.container import Container


@inject
async def Authorization(
    scopes: SecurityScopes,
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    auth_service: auth.LocalAuthService = Depends(Provide[Container.auth_service]),
) -> ClientCredentials:
    return await auth.Authorization(auth_service)(scopes, credentials)
