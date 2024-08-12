from fastapi import Security
from fastapi.routing import APIRouter

from db.models import ApprovalStatus
from db import service
from db.schemas import BidRecordSchema
from bot.handlers.bids.utils import get_current_coordinator

from api.auth import User, get_current_user


router = APIRouter()


@router.get("/")
async def get_bids(
    _: User = Security(get_current_user, scopes=["crm_bid"]),
) -> list[BidRecordSchema]:
    return service.get_bid_records()


@router.patch("/approve/{id}")
async def approve_bid(
    id: int, _: User = Security(get_current_user, scopes=["crm_bid"])
) -> BidRecordSchema:
    """Approves bid by `id`"""
    bid = service.get_bid_by_id(id)
    if bid:
        await service.update_bid_state(
            bid, get_current_coordinator(bid), ApprovalStatus.approved
        )
    return service.bid_to_bid_record(bid)


@router.patch("/reject/{id}")
async def reject_bid(
    id: int, reason: str, _: User = Security(get_current_user, scopes=["crm_bid"])
) -> BidRecordSchema:
    """Rejects bid by `id`"""
    bid = service.get_bid_by_id(id)
    if bid:
        bid.denying_reason = reason
        await service.update_bid_state(
            bid, get_current_coordinator(bid), ApprovalStatus.denied
        )
    return service.bid_to_bid_record(bid)


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
