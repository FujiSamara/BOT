from logging import Logger
from dependency_injector import providers, containers

from common.containers.auth import LocalAuthContainer
from common.containers.postgres import PostgresContainer
from common.auth import LocalAuthService
from common.http.auth import AuthHTTPClient


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    logger = providers.Dependency(Logger)

    postgres_container = providers.Container(PostgresContainer, config=config)
    auth_container = providers.Container(LocalAuthContainer, config=config)

    auth_service = providers.Factory(
        LocalAuthService, auth_container.container.security_client
    )

    auth_client = providers.Factory(
        AuthHTTPClient,
        auth_service,
        auth_url=config.auth_url,
        client_id=config.client_id,
        client_secret=config.client_secret,
        with_ssl=config.with_auth_ssl,
    )
