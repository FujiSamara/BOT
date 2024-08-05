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
):
    """Approves bid by `id`"""
    bid = service.get_bid_by_id(id)
    if bid:
        await service.update_bid_state(
            bid, get_current_coordinator(bid), ApprovalStatus.approved
        )


@router.patch("/reject/{id}")
async def reject_bid(id: int, _: User = Security(get_current_user, scopes=["crm_bid"])):
    """Rejects bid by `id`"""
    bid = service.get_bid_by_id(id)
    if bid:
        await service.update_bid_state(
            bid, get_current_coordinator(bid), ApprovalStatus.denied
        )
