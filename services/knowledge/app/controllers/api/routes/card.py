from logging import Logger
from fastapi import APIRouter, Depends, Security, HTTPException, status
from dependency_injector.wiring import Provide, inject
import traceback

from common.schemas.client_credential import ClientCredentials
from app.container import Container
from app.controllers.api.dependencies import Authorization
from app.infra.config.scopes import Scopes

from app.schemas.card import BusinessCardOutSchema
from app.contracts.services import CardService


router = APIRouter()


@router.get("/{id}")
@inject
async def get_card_by_id(
    id: int,
    service: CardService = Depends(Provide[Container]),
    logger: Logger = Depends(Provide[Container.logger]),
    _: ClientCredentials = Security(
        Authorization,
        scopes=[Scopes.CardRead.value],
    ),
) -> BusinessCardOutSchema | None:
    try:
        return await service.get_card_by_id(id)
    except Exception as e:
        logger.error("\n".join([str(e), traceback.format_exc()]))
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
