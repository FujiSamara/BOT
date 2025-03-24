from fastapi import APIRouter, Security, Depends
from dependency_injector.wiring import Provide, inject

from common.schemas.client_credential import ClientCredentials

from app.schemas.division import DivisionOutSchema
from app.contracts.services import DivisionService

from app.container import Container
from app.controllers.api.dependencies import Authorization
from app.infra.config.scopes import Scopes

router = APIRouter()


@router.get("/{id}")
@inject
async def get_division_by_id(
    id: int,
    service: DivisionService = Depends(Provide[Container.division_service]),
    _: ClientCredentials = Security(
        Authorization,
        scopes=[Scopes.DivisionRead.value],
    ),
) -> DivisionOutSchema | None:
    return await service.get_division_by_id(id)
