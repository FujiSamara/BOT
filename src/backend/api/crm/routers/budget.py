from typing import Optional
from fastapi import Security
from fastapi.routing import APIRouter

from db import service
from db.schemas import BudgetRecordSchema, BudgetRecordWithChapter

from api.auth import User, get_current_user


router = APIRouter()


@router.get("/")
async def get_budget_records(
    _: User = Security(get_current_user, scopes=["budget"]),
) -> list[BudgetRecordWithChapter]:
    return [
        BudgetRecordWithChapter(
            id=record.id,
            expenditure=record.expenditure,
            limit=record.limit,
            last_update=record.last_update,
            department=record.department,
            chapter=record.expenditure.chapter,
        )
        for record in service.get_budget_records()
    ]


@router.get("/last")
async def get_last_budget_record(
    _: User = Security(get_current_user, scopes=["budget"]),
) -> Optional[BudgetRecordWithChapter]:
    record = service.get_last_budget_record()
    if record:
        return BudgetRecordWithChapter(
            id=record.id,
            expenditure=record.expenditure,
            limit=record.limit,
            last_update=record.last_update,
            department=record.department,
            chapter=record.expenditure.chapter,
        )
    return None


@router.delete("/{id}")
async def delete_budget_record(
    id: int, _: User = Security(get_current_user, scopes=["budget"])
) -> None:
    service.remove_budget_record(id)


@router.patch("/")
async def update_budget_record(
    schema: BudgetRecordSchema, _: User = Security(get_current_user, scopes=["budget"])
) -> None:
    service.update_budget_record(schema)
