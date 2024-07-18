from typing import Annotated, Callable
from fastapi import Depends
from fastapi.routing import APIRouter

from db.schemas import PanelSchema

from api.crm.dependency import PanelParser

router = APIRouter()


@router.get("/{panel_name}s")
async def get_panel_rows(
    get_rows: Annotated[
        Callable[[], PanelSchema], Depends(PanelParser.build_getting_panels)
    ],
) -> PanelSchema:
    return get_rows()


@router.post("/{panel_name}/create")
async def create_panel_row(
    row: dict[str, str],
    create_row: Annotated[
        Callable[[dict[str, str]], None], Depends(PanelParser.build_creating_panel_row)
    ],
) -> None:
    create_row(row)


@router.delete("/{panel_name}/delete")
async def delete_panel_row(
    rowID: int,
    delete_row: Annotated[
        Callable[[int], None], Depends(PanelParser.build_deleting_panel_row)
    ],
) -> None:
    delete_row(rowID)


@router.patch("/{panel_name}/update")
async def update_panel_row(
    rowID: int,
    row: dict[str, str],
    create_row: Annotated[
        Callable[[int, dict[str, str]], None],
        Depends(PanelParser.build_updating_panel_row),
    ],
) -> None:
    create_row(rowID, row)
