from fastapi import Security
from fastapi.routing import APIRouter

from db.models import ApprovalStatus
from db import service
from db.schemas import BidRecordSchema, QuerySchema, TalbeInfoSchema
from bot.handlers.bids.utils import get_current_coordinator

from api.auth import User, get_current_user


router = APIRouter()


@router.post("/page/info")
async def get_pages_info(
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


@router.get("/fac/")
async def get_fac_bids(
    user: User = Security(get_current_user, scopes=["crm_fac_bid"]),
) -> list[BidRecordSchema]:
    return service.get_fac_bid_records_by_fac_phone(user.username)


@router.get("/cc/")
async def get_cc_bids(
    user: User = Security(get_current_user, scopes=["crm_cc_bid"]),
) -> list[BidRecordSchema]:
    return service.get_fac_bid_records_by_cc_phone(user.username)


@router.get("/cc_supervisor/")
async def get_cc_supervisor_bids(
    user: User = Security(get_current_user, scopes=["crm_cc_supervisor_bid"]),
) -> list[BidRecordSchema]:
    return service.get_fac_bid_records_by_cc_supervisor_phone(user.username)
