from typing import Optional
from fastapi import Security
from fastapi.routing import APIRouter

from app import services
from app.infra.database.schemas import (
    BudgetRecordSchema,
    BudgetRecordWithChapter,
    QuerySchema,
    TalbeInfoSchema,
)

from app.adapters.input.api.auth import User, get_user


router = APIRouter()


@router.post("/page/info")
async def get_pages_info(
    query: QuerySchema,
    records_per_page: int = 15,
    _: User = Security(get_user, scopes=["crm_budget"]),
) -> TalbeInfoSchema:
    record_count = services.get_budget_records_count(query)
    all_record_count = services.get_budget_records_count(QuerySchema())
    page_count = (record_count + records_per_page - 1) // records_per_page

    return TalbeInfoSchema(
        record_count=record_count,
        page_count=page_count,
        all_record_count=all_record_count,
    )


@router.post("/page/{page}")
async def get_bid_records(
    page: int,
    query: QuerySchema,
    records_per_page: int = 15,
    _: User = Security(get_user, scopes=["crm_budget"]),
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
        for record in services.get_budget_records_at_page(page, records_per_page, query)
    ]


@router.get("/last")
async def get_last_budget_record(
    _: User = Security(get_user, scopes=["crm_budget"]),
) -> Optional[BudgetRecordWithChapter]:
    record = services.get_last_budget_record()
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
    id: int, _: User = Security(get_user, scopes=["crm_budget"])
) -> None:
    services.remove_budget_record(id)


@router.patch("/")
async def update_budget_record(
    schema: BudgetRecordSchema,
    _: User = Security(get_user, scopes=["crm_budget"]),
) -> None:
    services.update_budget_record(schema)
