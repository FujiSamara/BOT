from fastapi import Security
from fastapi.routing import APIRouter

from db import service
from db.schemas import BidRecordSchema

from api.auth import User, get_current_user


router = APIRouter()


@router.get("/")
async def get_bids(
    _: User = Security(get_current_user, scopes=["bid"]),
) -> list[BidRecordSchema]:
    return service.get_bid_records()
