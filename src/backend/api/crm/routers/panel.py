from typing import Any, Callable
from fastapi.routing import APIRouter

from db import service
from db.schemas import BaseSchema, PanelSchema, ExpenditureSchema


router = APIRouter()


@router.get("/{panel_name}s")
async def get_panel_rows(panel_name: str) -> PanelSchema:
    get_schemas: Callable[[], list[BaseSchema]] | None = None

    match panel_name:
        case "expenditure":
            get_schemas = service.get_expenditures

    if get_schemas:
        return PanelSchema(dumps=[model.model_dump() for model in get_schemas()])
    else:
        return PanelSchema(dumps=[])


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

    create_schema(schema)


@router.delete("/{panel_name}/delete")
async def delete_panel_row(
    panel_name: str,
    rowID: int,
) -> None:
    pass


@router.patch("/{panel_name}/update")
async def update_panel_row(
    panel_name: str,
    rowID: int,
    row: dict[str, str],
) -> None:
    pass
