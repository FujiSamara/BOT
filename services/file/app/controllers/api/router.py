from logging import Logger
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, Security, status, Query
from dependency_injector.wiring import Provide, inject
import json
import hmac
import hashlib

from common.schemas.client_credential import ClientCredentials
from common.schemas.file import FileInSchema
from app.container import Container
from app.contracts.services import FileService
from app.schemas.file import FileConfirmSchema, FileDeleteResultSchema
from common.schemas.file import FileLinkSchema

from app.controllers.api.dependencies import Authorization
from app.infra.config.scopes import Scopes

router = APIRouter()


@router.post(
    "/",
    response_description="Created url with file ids",
)
@inject
async def create_put_links(
    files: list[FileInSchema],
    expiration: int = 3600,
    file_service: FileService = Depends(Provide[Container.file_service]),
    _: ClientCredentials = Security(
        Authorization,
        scopes=[Scopes.FileWrite.value],
    ),
) -> list[FileLinkSchema]:
    """Creates presigned urls for putting files with specified meta."""
    return await file_service.create_put_links(files, expiration)


@router.get(
    "/",
    response_description="Created urls with file meta",
)
@inject
async def create_get_links(
    ids: Annotated[list[int], Query()],
    expiration: int = 3600,
    file_service: FileService = Depends(Provide[Container.file_service]),
    _: ClientCredentials = Security(
        Authorization,
        scopes=[Scopes.FileRead.value],
    ),
) -> list[FileLinkSchema]:
    """Create presigned urls for getting files with specified meta."""
    return await file_service.create_get_links(ids, expiration)


@router.delete(
    "/",
)
@inject
async def delete_files(
    ids: Annotated[list[int], Query()],
    file_service: FileService = Depends(Provide[Container.file_service]),
    logger: Logger = Depends(Provide[Container.logger]),
    _: ClientCredentials = Security(
        Authorization,
        scopes=[Scopes.FileWrite.value],
    ),
) -> list[FileDeleteResultSchema]:
    """Delete files by specified `ids`.

    Returns:
        A list of `FileDeleteResultSchema` objects describing the files that failed to be deleted.
    """
    results = await file_service.delete_files(ids)
    if any([result.error is not None for result in results]):
        error_msg = "Several files not deleted:\n"
        files_msg = "\n".join(
            [
                f"ID: [{result.file_id}], {result.error.message}"
                for result in results
                if result.error is not None
            ]
        )
        logger.warning(error_msg + files_msg)
    return results


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
        event_name: str = record["eventName"]
        if "s3:ObjectCreated" not in event_name:
            continue

        s3 = record["s3"]
        bucket: str = s3["bucket"]["name"]
        obj: dict = s3["object"]
        key = obj["key"]
        size = obj.get("size", 0)

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
