from fastapi import APIRouter, Depends, Security
from dependency_injector.wiring import Provide, inject

from common.schemas.client_credential import ClientCredentials
from app.container import Container
from app.contracts.services import FileService
from app.schemas.file import FileInSchema

from app.controllers.api.dependencies import Authorization
from app.infra.config.scopes import Scopes

router = APIRouter()


@router.post(
    "/",
    description="Creates presigned url for putting file with specified meta.",
    response_description="Created url",
)
@inject
async def create_put_link(
    file: FileInSchema,
    file_service: FileService = Depends(Provide[Container.file_service]),
    _: ClientCredentials = Security(
        Authorization,
        scopes=[Scopes.FileRead.value],
    ),
) -> str:
    return await file_service.create_put_link(file)


@router.get(
    "/{id}",
    description="Creates presigned url for getting file with specified meta.",
    response_description="Created url",
)
@inject
async def create_get_link(
    id: int,
    file_service: FileService = Depends(Provide[Container.file_service]),
    _: ClientCredentials = Security(
        Authorization,
        scopes=[Scopes.FileRead.value],
    ),
) -> str:
    return await file_service.create_get_link(id)
