from logging import Logger
from contextlib import asynccontextmanager
from typing import AsyncIterator
import aioboto3
from mypy_boto3_s3 import ServiceResource
from dependency_injector import providers, containers

from common.containers.auth import LocalAuthContainer
from common.containers.postgres import PostgresContainer
from common.auth import LocalAuthService

from app.infra.database.uow import SQLFileUnitOfWork
from app.infra.s3.file import S3FileClient
from app.services.file import FileServiceImpl


def create_resource_factory(
    session: aioboto3.Session,
    aws_access_key_id: str,
    aws_secret_access_key: str,
    endpoint_url: str,
    region: str,
):
    @asynccontextmanager
    async def create_resource() -> AsyncIterator[ServiceResource]:
        async with session.resource(
            service_name="s3",
            region_name=region,
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        ) as r:
            yield r

    return create_resource


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    logger = providers.Dependency(Logger)

    postgres_container = providers.Container(PostgresContainer, config=config)
    auth_container = providers.Container(LocalAuthContainer, config=config)

    auth_service = providers.Resource(
        LocalAuthService, auth_container.container.security_client
    )

    s3_session = providers.Factory(aioboto3.Session)
    s3_resource_factory = providers.Factory(
        create_resource_factory,
        session=s3_session,
        aws_access_key_id=config.access_key,
        aws_secret_access_key=config.secret_access_key,
        region=config.region,
        endpoint_url=config.endpoint_url,
    )
    s3_client = providers.Factory(S3FileClient, s3_resource_factory)

    file_uow = providers.Factory(
        SQLFileUnitOfWork, postgres_container.container.async_sessionmaker
    )

    file_service = providers.Factory(
        FileServiceImpl, file_uow, s3_client, config.buckets
    )
