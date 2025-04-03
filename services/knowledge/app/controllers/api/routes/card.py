from logging import Logger
from fastapi import APIRouter, Depends, Security, HTTPException, status
from dependency_injector.wiring import Provide, inject
import traceback

from common.schemas.file import FileLinkSchema
from common.schemas.client_credential import ClientCredentials
from app.container import Container
from app.controllers.api.dependencies import Authorization
from app.infra.config.scopes import Scopes

from app.schemas.card import BusinessCardSchema
from app.schemas.file import FileInSchema
from app.contracts.services import CardService


router = APIRouter()


@router.get("/{id}")
@inject
async def get_card_by_id(
    id: int,
    service: CardService = Depends(Provide[Container.card_service]),
    logger: Logger = Depends(Provide[Container.logger]),
    _: ClientCredentials = Security(
        Authorization,
        scopes=[Scopes.CardRead.value],
    ),
) -> BusinessCardSchema | None:
    try:
        return await service.get_card_by_id(id)
    except Exception as e:
        logger.error("\n".join([str(e), traceback.format_exc()]))
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{id}/materials")
@inject
async def get_card_materials(
    id: int,
    service: CardService = Depends(Provide[Container.card_service]),
    logger: Logger = Depends(Provide[Container.logger]),
    _: ClientCredentials = Security(
        Authorization,
        scopes=[Scopes.DishRead.value],
    ),
) -> list[FileLinkSchema]:
    try:
        return await service.get_card_materials(id)
    except Exception as e:
        logger.error("\n".join([str(e), traceback.format_exc()]))
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{id}/materials")
@inject
async def add_card_materials(
    id: int,
    materials: list[FileInSchema],
    service: CardService = Depends(Provide[Container.card_service]),
    logger: Logger = Depends(Provide[Container.logger]),
    _: ClientCredentials = Security(
        Authorization,
        scopes=[Scopes.CardWrite.value],
    ),
):
    try:
        return await service.add_card_materials(id, materials)
    except ValueError as e:
        logger.error("\n".join([str(e), traceback.format_exc()]))
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error("\n".join([str(e), traceback.format_exc()]))
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
