from typing import Optional
from fastapi.routing import APIRouter

from db import service
from db.schemas import BudgetRecordSchema


router = APIRouter()


@router.get("/")
async def get_budget_records() -> list[BudgetRecordSchema]:
    return service.get_budget_records()


@router.get("/last")
async def get_last_budget_record() -> Optional[BudgetRecordSchema]:
    return service.get_last_budget_record()


@router.get("/{id}")
async def get_budget_record(id: int) -> Optional[BudgetRecordSchema]:
    return service.get_budget_record_by_id(id)


@router.delete("/{id}")
async def delete_budget_record(
    id: int,
) -> None:
    service.remove_budget_record(id)


@router.patch("/")
async def update_budget_record(
    schema: BudgetRecordSchema,
) -> None:
    service.update_budget_record(schema)
