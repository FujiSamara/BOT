from fastapi import Security
from fastapi.routing import APIRouter

from db import service
from db.schemas import (
    WorkTimeSchema,
    QuerySchema,
    TalbeInfoSchema,
)

from api.auth import User, get_current_user


router = APIRouter()


@router.post("/page/info")
async def get_pages_info(
    query: QuerySchema,
    records_per_page: int = 15,
    _: User = Security(get_current_user, scopes=["crm_worktime"]),
) -> TalbeInfoSchema:
    record_count = service.get_wortkime_count(query)
    all_record_count = service.get_wortkime_count(QuerySchema())
    page_count = (record_count + records_per_page - 1) // records_per_page

    return TalbeInfoSchema(
        record_count=record_count,
        page_count=page_count,
        all_record_count=all_record_count,
    )


@router.post("/page/{page}")
async def get_worktimes(
    page: int,
    query: QuerySchema,
    records_per_page: int = 15,
    _: User = Security(get_current_user, scopes=["crm_worktime"]),
) -> list[WorkTimeSchema]:
    return service.get_worktimes_at_page(page, records_per_page, query)


@router.delete("/{id}")
async def delete_worktime(
    id: int, _: User = Security(get_current_user, scopes=["crm_worktime"])
) -> None:
    service.remove_worktime(id)


@router.patch("/")
async def update_budget_record(
    schema: WorkTimeSchema,
    _: User = Security(get_current_user, scopes=["crm_worktime"]),
) -> None:
    service.update_worktime(schema)
