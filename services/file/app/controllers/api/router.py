from logging import Logger
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Security,
    status,
)
from dependency_injector.wiring import Provide, inject
import json
import hmac
import hashlib

from common.schemas.client_credential import ClientCredentials
from app.container import Container
from app.contracts.services import FileService
from app.schemas.file import FileInSchema, FileConfirmSchema
from common.schemas.file import FileLinkSchema

from app.controllers.api.dependencies import Authorization
from app.infra.config.scopes import Scopes

router = APIRouter()


@router.post(
    "/",
    response_description="Created url with file id",
)
@inject
async def create_put_link(
    file: FileInSchema,
    expiration: int = 3600,
    file_service: FileService = Depends(Provide[Container.file_service]),
    _: ClientCredentials = Security(
        Authorization,
        scopes=[Scopes.FileRead.value],
    ),
) -> FileLinkSchema:
    """Creates presigned url for putting file with specified meta."""
    try:
        link = await file_service.create_put_link(file, expiration)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return link


@router.get(
    "/{id}",
    response_description="Created url with file id",
)
@inject
async def create_get_link(
    id: int,
    expiration: int = 3600,
    file_service: FileService = Depends(Provide[Container.file_service]),
    _: ClientCredentials = Security(
        Authorization,
        scopes=[Scopes.FileRead.value],
    ),
) -> FileLinkSchema:
    """Creates presigned url for getting file with specified meta."""
    try:
        link = await file_service.create_get_link(id, expiration)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return link


@router.post("/s3_webhook")
async def s3_webhook(
    request: Request,
):
    """Webhook specified for vkcloud s3 events."""
    body = await request.body()
    data = json.loads(body)

    if "Type" in data:
        return await confirm_subscription(request)
    else:
        return await got_records(data)


@inject
async def got_records(
    data: dict,
    file_service: FileService = Provide[Container.file_service],
    logger: Logger = Provide[Container.logger],
):
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
            logger.error(f"Error while confirmation file: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@inject
async def confirm_subscription(
    request: Request,
    config=Provide[Container.config],
):
    method = hashlib.sha256

    def hmacsha256(message: bytes, secret: bytes) -> bytes:
        return hmac.new(secret, message, method).digest()

    def hmacsha256hex(message: bytes, secret: bytes) -> str:
        return hmac.new(secret, message, method).hexdigest()

    body = await request.body()
    data = json.loads(body)
    url = config["url"] + request.url.path
    return {
        "signature": hmacsha256hex(
            url.encode(),
            hmacsha256(
                data["TopicArn"].encode(),
                hmacsha256(
                    data["Timestamp"].encode(),
                    data["Token"].encode(),
                ),
            ),
        )
    }
