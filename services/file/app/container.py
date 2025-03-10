from logging import Logger
from dependency_injector import providers, containers

from common.containers.auth import LocalAuthContainer
from common.containers.postgres import PostgresContainer
from common.auth import LocalAuthService

from app.infra.database.uow import SQLFileUnitOfWork
from app.services.file import FileServiceImpl


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    logger = providers.Dependency(Logger)

    postgres_container = providers.Container(PostgresContainer, config=config)
    auth_container = providers.Container(LocalAuthContainer, config=config)

    auth_service = providers.Resource(
        LocalAuthService, auth_container.container.security_client
    )

    file_uow = providers.Factory(
        SQLFileUnitOfWork, postgres_container.container.async_sessionmaker
    )

    file_service = providers.Factory(FileServiceImpl, file_uow)
