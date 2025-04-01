from logging import Logger
from fastapi import APIRouter, Depends, Security, HTTPException, status
from dependency_injector.wiring import Provide, inject
import traceback

from common.schemas.client_credential import ClientCredentials
from app.container import Container
from app.controllers.api.dependencies import Authorization
from app.infra.config.scopes import Scopes

from app.schemas.dish import DishSchema, DishModifierSchema, DishMaterialsSchema
from app.contracts.services import DishService

router = APIRouter()


@router.get("/{id}")
@inject
async def get_dish_by_id(
    id: int,
    service: DishService = Depends(Provide[Container.dish_service]),
    logger: Logger = Depends(Provide[Container.logger]),
    _: ClientCredentials = Security(
        Authorization,
        scopes=[Scopes.DishRead.value],
    ),
) -> DishSchema | None:
    try:
        return await service.get_dish_by_id(id)
    except Exception as e:
        logger.error("\n".join([str(e), traceback.format_exc()]))
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{id}/modifier")
@inject
async def get_dish_modifiers(
    id: int,
    service: DishService = Depends(Provide[Container.dish_service]),
    logger: Logger = Depends(Provide[Container.logger]),
    _: ClientCredentials = Security(
        Authorization,
        scopes=[Scopes.DishRead.value],
    ),
) -> list[DishModifierSchema]:
    try:
        return await service.get_dish_modifiers(id)
    except Exception as e:
        logger.error("\n".join([str(e), traceback.format_exc()]))
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{id}/materials")
@inject
async def get_dish_materials(
    id: int,
    service: DishService = Depends(Provide[Container.dish_service]),
    logger: Logger = Depends(Provide[Container.logger]),
    _: ClientCredentials = Security(
        Authorization,
        scopes=[Scopes.DishRead.value],
    ),
) -> DishMaterialsSchema:
    try:
        return await service.get_dish_materials(id)
    except Exception as e:
        logger.error("\n".join([str(e), traceback.format_exc()]))
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
