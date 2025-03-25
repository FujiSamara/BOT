from logging import Logger
from fastapi import APIRouter, Security, Depends, HTTPException, status
from dependency_injector.wiring import Provide, inject
import traceback

from common.schemas.client_credential import ClientCredentials
from app.container import Container
from app.controllers.api.dependencies import Authorization
from app.infra.config.scopes import Scopes

from app.schemas.division import DivisionOutSchema
from app.contracts.services import DivisionService

router = APIRouter()


@router.get("/")
@inject
async def get_division_by_path(
    path: str,
    service: DivisionService = Depends(Provide[Container.division_service]),
    logger: Logger = Depends(Provide[Container.logger]),
    _: ClientCredentials = Security(
        Authorization,
        scopes=[Scopes.DivisionRead.value],
    ),
) -> DivisionOutSchema | None:
    try:
        return await service.get_division_by_path(path)
    except Exception as e:
        logger.error("\n".join([str(e), traceback.format_exc()]))
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
