from fastapi import Response, Security
from fastapi.responses import StreamingResponse
from fastapi.routing import APIRouter

import app.db.service.worktime as service
from app.db.schemas import (
    WorkTimeSchema,
    QuerySchema,
    TalbeInfoSchema,
    WorkTimeSchemaFull,
)

from app.adapters.input.api.auth import User, get_user


router = APIRouter()


@router.post("/page/info")
async def get_pages_info(
    query: QuerySchema,
    records_per_page: int = 15,
    _: User = Security(get_user, scopes=["crm_worktime"]),
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
    _: User = Security(get_user, scopes=["crm_worktime"]),
) -> list[WorkTimeSchemaFull]:
    return service.get_worktimes_at_page(page, records_per_page, query)


@router.post("/")
async def create_worktime(
    schema: WorkTimeSchema,
    _: User = Security(get_user, scopes=["crm_worktime"]),
) -> None:
    await service.create_worktime(schema)


@router.delete("/{id}")
async def delete_worktime(
    id: int, _: User = Security(get_user, scopes=["crm_worktime"])
) -> None:
    await service.remove_worktime(id)


@router.patch("/")
async def update_worktime(
    schema: WorkTimeSchema,
    _: User = Security(get_user, scopes=["crm_worktime"]),
) -> None:
    await service.update_worktime(schema)


@router.post("/export")
async def export_worktimes(
    query: QuerySchema, _: User = Security(get_user, scopes=["crm_worktime"])
) -> Response:
    file = service.export_worktimes(query)

    return StreamingResponse(
        content=file,
        headers={
            "Content-Disposition": "filename=worktimes.xlsx",
        },
        media_type="application/octet-stream",
    )


@router.get("/download_photo/{photo_id}")
async def get_worktime_photo(
    photo_id: int, _: User = Security(get_user, scopes=["crm_worktime"])
) -> Response:
    photo = service.get_worktime_photo_by_id(photo_id)
    return StreamingResponse(
        content=photo,
        headers={
            "Content-Disposition": f"filename=photo_{photo_id}.jpg",
        },
        media_type="application/octet-stream",
    )
