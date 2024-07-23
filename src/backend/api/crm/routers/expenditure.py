from typing import Optional
from fastapi.routing import APIRouter

from db import service
from db.schemas import ExpenditureSchema


router = APIRouter()


@router.get("/")
async def get_expenditures() -> list[ExpenditureSchema]:
    return service.get_expenditures()


@router.get("/last")
async def get_last_expenditure() -> Optional[ExpenditureSchema]:
    return service.get_last_expenditure()


@router.get("/{id}")
async def get_expenditure(id: int) -> Optional[ExpenditureSchema]:
    return service.get_expenditure_by_id(id)


@router.post("/")
async def create_expenditure(
    schema: ExpenditureSchema,
) -> None:
    service.create_expenditure(schema)


@router.delete("/{id}")
async def delete_expenditure(
    id: int,
) -> None:
    service.remove_expenditure(id)


@router.patch("/update")
async def update_expenditure(
    schema: ExpenditureSchema,
) -> None:
    service.update_expenditure(schema)
