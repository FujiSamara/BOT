from logging import Logger
from dependency_injector import providers, containers
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession

from common.containers.auth import LocalAuthContainer
from common.containers.postgres import PostgresContainer
from common.auth import LocalAuthService
from common.http.auth import AuthHTTPClient
from common.http.file import HTTPFileClient

from app.infra.database.uow import SQLDivisionUnitOfWork
from app.infra.database.binds import get_tables_binds
from app.services.division import DivisionServiceImpl
from app.services.card import CardServiceImpl


def init_sessionmaker(
    dish_engine: AsyncEngine, knowledge_engine: AsyncEngine
) -> async_sessionmaker[AsyncSession]:
    maker = async_sessionmaker()
    maker.configure(binds=get_tables_binds(dish_engine, knowledge_engine))
    return maker


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    logger = providers.Dependency(Logger)

    postgres_knowledge_container = providers.Container(PostgresContainer, config=config)
    postgres_dish_container = providers.Container(PostgresContainer, config=config)
    auth_container = providers.Container(LocalAuthContainer, config=config)

    sessionmaker = providers.Singleton(
        init_sessionmaker,
        postgres_dish_container.container.async_engine,
        postgres_knowledge_container.container.async_engine,
    )

    uow = providers.Factory(SQLDivisionUnitOfWork, sessionmaker)

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
    file_client = providers.Factory(
        HTTPFileClient,
        auth_client,
        file_service_url=config.file_url,
        with_ssl=config.with_file_ssl,
    )

    division_service = providers.Factory(DivisionServiceImpl, uow)
    card_service = providers.Factory(CardServiceImpl, uow)
