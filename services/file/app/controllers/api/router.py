from fastapi import APIRouter, Security
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
    _: ClientCredentials = Security(
        Authorization,
        scopes=[Scopes.FileRead.value],
    ),
) -> str:
    print(_)
    return "Hello world!"
