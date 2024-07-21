from typing import Any, Callable
from fastapi.routing import APIRouter
from fastapi.exceptions import HTTPException

from db import service
from db.schemas import BaseSchema, PanelSchema, ExpenditureSchema


router = APIRouter()


@router.get("/{panel_name}s")
async def get_panel_rows(panel_name: str) -> PanelSchema:
    get_schemas: Callable[[], list[BaseSchema]] | None = None

    match panel_name:
        case "expenditure":
            get_schemas = service.get_expenditures
        case _:
            return HTTPException(400)

    return PanelSchema(dumps=[model.model_dump() for model in get_schemas()])


@router.get("/{panel_name}/{id}")
async def get_panel_row(panel_name: str, id: int) -> dict[str, Any]:
    get_schema: Callable[[], BaseSchema] | None = None

    match panel_name:
        case "expenditure":
            get_schema = service.get_expenditure_by_id
        case _:
            return HTTPException(400)

    model = get_schema(id)
    if model:
        return model.model_dump()
    return None


@router.post("/{panel_name}/create")
async def create_panel_row(
    panel_name: str,
    row: dict[str, Any],
) -> None:
    create_schema: Callable[[BaseSchema], None] | None = None
    schema: BaseSchema | None = None

    match panel_name:
        case "expenditure":
            schema = ExpenditureSchema.model_validate(row)
            create_schema = service.create_expenditure
        case _:
            return HTTPException(400)

    create_schema(schema)


@router.delete("/{panel_name}/delete")
async def delete_panel_row(
    panel_name: str,
    rowID: int,
) -> None:
    pass
    remove_schema: Callable[[int]] | None = None

    match panel_name:
        case "expenditure":
            remove_schema = service.remove_expenditure
        case _:
            return HTTPException(400)

    remove_schema(rowID)


@router.patch("/{panel_name}/update")
async def update_panel_row(
    panel_name: str,
    row: dict[str, Any],
) -> None:
    update_schema: Callable[[BaseSchema], None] | None = None
    schema: BaseSchema | None = None

    match panel_name:
        case "expenditure":
            schema = ExpenditureSchema.model_validate(row)
            update_schema = service.update_expenditure
        case _:
            return HTTPException(400)

    update_schema(schema)
