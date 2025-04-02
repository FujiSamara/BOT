from dependency_injector import containers, providers

from common.auth.security import PyJWTSecurityClient
from common.containers.base import BaseContainer


@containers.copy(BaseContainer)
class LocalAuthContainer(BaseContainer):
    security_client = providers.Singleton(
        PyJWTSecurityClient,
        BaseContainer.config.public_key,
        BaseContainer.config.private_key,
    )
