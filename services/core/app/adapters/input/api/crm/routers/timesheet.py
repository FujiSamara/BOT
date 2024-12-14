from fastapi import Security
from fastapi.routing import APIRouter

from app.services import timesheet
from app.schemas import (
    TimeSheetSchema,
    QuerySchema,
    TalbeInfoSchema,
)

from app.adapters.input.api.auth import User, get_user


router = APIRouter()


@router.post("/page/info")
async def get_pages_info(
    query: QuerySchema,
    records_per_page: int = 15,
    _: User = Security(get_user, scopes=["authenticated"]),
) -> TalbeInfoSchema:
    record_count = timesheet.get_timesheet_count(query)
    all_record_count = timesheet.get_timesheet_count(QuerySchema())
    page_count = (record_count + records_per_page - 1) // records_per_page

    return TalbeInfoSchema(
        record_count=record_count,
        page_count=page_count,
        all_record_count=all_record_count,
    )


@router.post("/page/{page}")
async def get_timesheets(
    page: int,
    query: QuerySchema,
    records_per_page: int = 15,
    _: User = Security(get_user, scopes=["authenticated"]),
) -> list[TimeSheetSchema]:
    return timesheet.get_timesheets_at_page(page, records_per_page, query)
