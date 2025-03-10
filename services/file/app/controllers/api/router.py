from fastapi import (
    APIRouter,
)
from dependency_injector.wiring import Provide, inject

from app.container import Container
from common.schemas.client_credential import ClientCredentials
from app.contracts.services import FileService

from app.controllers.api.dependencies import Authorization

router = APIRouter()
