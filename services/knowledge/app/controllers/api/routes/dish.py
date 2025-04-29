from logging import Logger
from typing import Annotated
from fastapi import APIRouter, Depends, Query, Security, HTTPException, status
from dependency_injector.wiring import Provide, inject
import traceback

from common.schemas.file import FileLinkSchema, FileUpdateResultSchema
from common.schemas.client_credential import ClientCredentials
from app.container import Container
from app.controllers.api.dependencies import Authorization
from app.infra.config.scopes import Scopes

from app.schemas.dish import DishSchema, DishModifierSchema, DishMaterialsSchema
from app.schemas.file import FileInSchema
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


@router.get("/{id}/modifiers")
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
    except ValueError as e:
        logger.error("\n".join([str(e), traceback.format_exc()]))
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
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
    except ValueError as e:
        logger.error("\n".join([str(e), traceback.format_exc()]))
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error("\n".join([str(e), traceback.format_exc()]))
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{id}/video")
@inject
async def add_dish_video(
    id: int,
    video: FileInSchema,
    service: DishService = Depends(Provide[Container.dish_service]),
    logger: Logger = Depends(Provide[Container.logger]),
    _: ClientCredentials = Security(
        Authorization,
        scopes=[Scopes.DishWrite.value],
    ),
) -> FileLinkSchema:
    """Create put link for dish video and registrated it in database."""
    try:
        return await service.add_dish_video(id, video)
    except ValueError as e:
        logger.error("\n".join([str(e), traceback.format_exc()]))
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error("\n".join([str(e), traceback.format_exc()]))
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{id}/materials")
@inject
async def add_dish_materials(
    id: int,
    materials: list[FileInSchema],
    service: DishService = Depends(Provide[Container.dish_service]),
    logger: Logger = Depends(Provide[Container.logger]),
    _: ClientCredentials = Security(
        Authorization,
        scopes=[Scopes.DishWrite.value],
    ),
) -> list[FileLinkSchema]:
    try:
        return await service.add_dish_materials(id, materials)
    except ValueError as e:
        logger.error("\n".join([str(e), traceback.format_exc()]))
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error("\n".join([str(e), traceback.format_exc()]))
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{id}/materials")
@inject
async def delete_dish_materials(
    id: int,
    ids: Annotated[list[int], Query()],
    service: DishService = Depends(Provide[Container.dish_service]),
    logger: Logger = Depends(Provide[Container.logger]),
    _: ClientCredentials = Security(
        Authorization,
        scopes=[Scopes.DishWrite.value],
    ),
):
    try:
        results = await service.delete_dish_materials(id, ids)
        if any([result.error is not None for result in results]):
            error_msg = "Several dish materials not deleted:\n"
            files_msg = "\n".join(
                [
                    f"ID: [{result.file_id}], {result.error.message}"
                    for result in results
                    if result.error is not None
                ]
            )
            logger.warning(error_msg + files_msg)
        return results
    except ValueError as e:
        logger.error("\n".join([str(e), traceback.format_exc()]))
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error("\n".join([str(e), traceback.format_exc()]))
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{id}/video")
@inject
async def update_dish_video(
    id: int,
    video: FileInSchema,
    service: DishService = Depends(Provide[Container.dish_service]),
    logger: Logger = Depends(Provide[Container.logger]),
    _: ClientCredentials = Security(
        Authorization,
        scopes=[Scopes.DishWrite.value],
    ),
) -> FileUpdateResultSchema:
    """Create put link for new dish video and registrated it in database.
    Also delete old video.
    """
    try:
        delete_result = await service.delete_dish_video(id)
        if delete_result.error is not None:
            return FileUpdateResultSchema(meta=None, error=delete_result.error)

        add_result = await service.add_dish_video(id, video)
        return FileUpdateResultSchema(meta=add_result, error=None)
    except ValueError as e:
        logger.error("\n".join([str(e), traceback.format_exc()]))
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error("\n".join([str(e), traceback.format_exc()]))
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
