from fastapi import APIRouter, Depends, HTTPException, Request, Security, status
from dependency_injector.wiring import Provide, inject
import json

from common.schemas.client_credential import ClientCredentials
from app.container import Container
from app.contracts.services import FileService
from app.schemas.file import FileInSchema, FileConfirmSchema

from app.controllers.api.dependencies import Authorization
from app.infra.config.scopes import Scopes

router = APIRouter()


@router.post(
    "/",
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
    """Creates presigned url for putting file with specified meta."""
    try:
        link = await file_service.create_put_link(file)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return link


@router.get(
    "/{id}",
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
    """Creates presigned url for getting file with specified meta."""
    try:
        link = await file_service.create_get_link(id)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return link


@router.post("/s3_webhook")
@inject
async def s3_webhook(
    request: Request,
    file_service: FileService = Depends(Provide[Container.file_service]),
):
    """Webhook specified for vkcloud s3 events."""
    body = await request.body()
    data = json.loads(body)
    records: list = data["Records"]

    for record in records:
        event_name = record["eventName"]
        if event_name != "s3:ObjectCreated:Put":
            continue

        s3 = record["s3"]
        bucket: str = s3["bucket"]["name"]
        key = s3["object"]["key"]
        size = s3["object"]["size"]

        file_confirm = FileConfirmSchema(key=key, bucket=bucket, size=size)

        try:
            await file_service.confirm_putting(file_confirm)
        except (ValueError, KeyError) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
