from fastapi import Response, Security
from fastapi.responses import StreamingResponse
from fastapi.routing import APIRouter

from db.models import ApprovalStatus
from db import service
from db.schemas import BidRecordSchema, QuerySchema, TalbeInfoSchema
from bot.handlers.bids.utils import get_current_coordinator

from api.auth import User, get_current_user


router = APIRouter()


@router.post("/page/info")
async def get_bid_pages_info(
    query: QuerySchema,
    records_per_page: int = 15,
    _: User = Security(get_current_user, scopes=["crm_bid"]),
) -> TalbeInfoSchema:
    record_count = service.get_bid_count(query)
    all_record_count = service.get_bid_count(QuerySchema())
    page_count = (record_count + records_per_page - 1) // records_per_page

    return TalbeInfoSchema(
        record_count=record_count,
        page_count=page_count,
        all_record_count=all_record_count,
    )


@router.post("/page/{page}")
async def get_bids(
    page: int,
    query: QuerySchema,
    records_per_page: int = 15,
    _: User = Security(get_current_user, scopes=["crm_bid"]),
) -> list[BidRecordSchema]:
    return service.get_bid_record_at_page(page, records_per_page, query)


@router.patch("/approve/{id}")
async def approve_bid(
    id: int, _: User = Security(get_current_user, scopes=["crm_bid"])
):
    """Approves bid by `id`"""
    bid = service.get_bid_by_id(id)
    if bid:
        await service.update_bid_state(
            bid, get_current_coordinator(bid), ApprovalStatus.approved
        )


@router.patch("/reject/{id}")
async def reject_bid(
    id: int, reason: str, _: User = Security(get_current_user, scopes=["crm_bid"])
):
    """Rejects bid by `id`"""
    bid = service.get_bid_by_id(id)
    if bid:
        bid.denying_reason = reason
        await service.update_bid_state(
            bid, get_current_coordinator(bid), ApprovalStatus.denied
        )


@router.post("/export")
async def export_bids(
    query: QuerySchema, _: User = Security(get_current_user, scopes=["crm_bid"])
) -> Response:
    file = service.export_bid_records(query)

    return StreamingResponse(
        content=file,
        headers={
            "Content-Disposition": "filename=bids.xlsx",
        },
        media_type="application/octet-stream",
    )


@router.post("/fac/page/info")
async def get_fac_bid_pages_info(
    query: QuerySchema,
    records_per_page: int = 15,
    user: User = Security(get_current_user, scopes=["crm_fac_bid"]),
) -> TalbeInfoSchema:
    record_count = service.get_coordinator_bid_count(query, user.username, "fac")
    all_record_count = service.get_coordinator_bid_count(
        QuerySchema(), user.username, "fac"
    )
    page_count = (record_count + records_per_page - 1) // records_per_page

    return TalbeInfoSchema(
        record_count=record_count,
        page_count=page_count,
        all_record_count=all_record_count,
    )


@router.post("/fac/page/{page}")
async def get_fac_bids(
    page: int,
    query: QuerySchema,
    records_per_page: int = 15,
    user: User = Security(get_current_user, scopes=["crm_fac_bid"]),
) -> list[BidRecordSchema]:
    return service.get_coordinator_bid_records_at_page(
        page, records_per_page, query, user.username, "fac"
    )


@router.post("/cc/page/info")
async def get_cc_bid_pages_info(
    query: QuerySchema,
    records_per_page: int = 15,
    user: User = Security(get_current_user, scopes=["crm_cc_bid"]),
) -> TalbeInfoSchema:
    record_count = service.get_coordinator_bid_count(query, user.username, "cc")
    all_record_count = service.get_coordinator_bid_count(
        QuerySchema(), user.username, "cc"
    )
    page_count = (record_count + records_per_page - 1) // records_per_page

    return TalbeInfoSchema(
        record_count=record_count,
        page_count=page_count,
        all_record_count=all_record_count,
    )


@router.post("/cc/page/{page}")
async def get_cc_bids(
    page: int,
    query: QuerySchema,
    records_per_page: int = 15,
    user: User = Security(get_current_user, scopes=["crm_cc_bid"]),
) -> list[BidRecordSchema]:
    return service.get_coordinator_bid_records_at_page(
        page, records_per_page, query, user.username, "cc"
    )


@router.post("/cc_supervisor/page/info")
async def get_cc_supervisor_bid_pages_info(
    query: QuerySchema,
    records_per_page: int = 15,
    user: User = Security(get_current_user, scopes=["crm_cc_supervisor_bid"]),
) -> TalbeInfoSchema:
    record_count = service.get_coordinator_bid_count(
        query, user.username, "cc_supervisor"
    )
    all_record_count = service.get_coordinator_bid_count(
        QuerySchema(), user.username, "cc_supervisor"
    )
    page_count = (record_count + records_per_page - 1) // records_per_page

    return TalbeInfoSchema(
        record_count=record_count,
        page_count=page_count,
        all_record_count=all_record_count,
    )


@router.post("/cc_supervisor/page/{page}")
async def get_cc_supervisor_bids(
    page: int,
    query: QuerySchema,
    records_per_page: int = 15,
    user: User = Security(get_current_user, scopes=["crm_cc_supervisor_bid"]),
) -> list[BidRecordSchema]:
    return service.get_coordinator_bid_records_at_page(
        page, records_per_page, query, user.username, "cc_supervisor"
    )


@router.post("/fac/export")
async def export_fac_bids(
    query: QuerySchema, user: User = Security(get_current_user, scopes=["crm_fac_bid"])
) -> Response:
    file = service.export_coordintator_bid_records(query, user.username, "fac")

    return StreamingResponse(
        content=file,
        headers={
            "Content-Disposition": "filename=bids.xlsx",
        },
        media_type="application/octet-stream",
    )


@router.post("/cc/export")
async def export_cc_bids(
    query: QuerySchema, user: User = Security(get_current_user, scopes=["crm_cc_bid"])
) -> Response:
    file = service.export_coordintator_bid_records(query, user.username, "cc")

    return StreamingResponse(
        content=file,
        headers={
            "Content-Disposition": "filename=bids.xlsx",
        },
        media_type="application/octet-stream",
    )


@router.post("/cc_supervisor/export")
async def export_cc_supervisor_bids(
    query: QuerySchema,
    user: User = Security(get_current_user, scopes=["crm_cc_supervisor_bid"]),
) -> Response:
    file = service.export_coordintator_bid_records(
        query, user.username, "cc_supervisor"
    )

    return StreamingResponse(
        content=file,
        headers={
            "Content-Disposition": "filename=bids.xlsx",
        },
        media_type="application/octet-stream",
    )
