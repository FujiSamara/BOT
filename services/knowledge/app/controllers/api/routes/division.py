from fastapi import APIRouter, Security
from dependency_injector.wiring import Provide, inject

from common.schemas.client_credential import ClientCredentials
from app.schemas.division import DivisionOutSchema

from app.controllers.api.dependencies import Authorization
from app.infra.config.scopes import Scopes

router = APIRouter()


@router.get("/{id}")
@inject
async def get_division_by_id(
    id: int,
    _: ClientCredentials = Security(
        Authorization,
        scopes=[Scopes.DivisionRead.value],
    ),
) -> DivisionOutSchema | None:
    pass
