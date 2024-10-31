from fastapi import Response, Security, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.routing import APIRouter

from db.models import ApprovalStatus
from db import service
from db.schemas import BidOutSchema, QuerySchema, TalbeInfoSchema, BidInSchema
from bot.handlers.bids.utils import get_current_coordinator_field

from api.auth import User, get_user


router = APIRouter()


# region bids
@router.post("/page/info")
async def get_bid_pages_info(
    query: QuerySchema,
    records_per_page: int = 15,
    _: User = Security(get_user, scopes=["crm_bid"]),
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
    _: User = Security(get_user, scopes=["crm_bid"]),
) -> list[BidOutSchema]:
    return service.get_bid_record_at_page(page, records_per_page, query)


@router.patch("/approve/{id}")
async def approve_bid(id: int, _: User = Security(get_user, scopes=["crm_bid"])):
    """Approves bid by `id`"""
    bid = service.get_bid_by_id(id)
    if bid:
        await service.update_bid_state(
            bid, get_current_coordinator_field(bid), ApprovalStatus.approved
        )


@router.patch("/reject/{id}")
async def reject_bid(
    id: int, reason: str, _: User = Security(get_user, scopes=["crm_bid"])
):
    """Rejects bid by `id`"""
    bid = service.get_bid_by_id(id)
    if bid:
        bid.denying_reason = reason
        await service.update_bid_state(
            bid, get_current_coordinator_field(bid), ApprovalStatus.denied
        )


@router.post("/export")
async def export_bids(
    query: QuerySchema, _: User = Security(get_user, scopes=["crm_bid"])
) -> Response:
    file = service.export_bid_records(query)

    return StreamingResponse(
        content=file,
        headers={
            "Content-Disposition": "filename=bids.xlsx",
        },
        media_type="application/octet-stream",
    )


@router.delete("/{id}")
async def delete_bid(
    id: int, _: User = Security(get_user, scopes=["authenticated"])
) -> None:
    service.remove_bid(id)


@router.post("/")
async def create_my_bid(
    bid: BidInSchema,
    user: User = Security(get_user, scopes=["authenticated"]),
) -> BidOutSchema:
    bid.worker = service.get_worker_by_phone_number(user.username)
    return await service.create_bid_by_in_schema(bid)


@router.post("/{id}")
async def add_document(
    id: int,
    files: list[UploadFile],
    _: User = Security(get_user, scopes=["authenticated"]),
):
    service.add_documents_to_bid(id, files)


# endregion


# region fac bids
@router.post("/fac/page/info")
async def get_fac_bid_pages_info(
    query: QuerySchema,
    records_per_page: int = 15,
    user: User = Security(get_user, scopes=["crm_fac_bid"]),
) -> TalbeInfoSchema:
    service.apply_bid_status_filter(query, "fac_state", ApprovalStatus.pending_approval)
    record_count = service.get_coordinator_bid_count(query, user.username, "fac")
    all_record_count = service.get_coordinator_bid_count(
        service.apply_bid_status_filter(
            QuerySchema(),
            "fac_state",
            ApprovalStatus.pending_approval,
            ApprovalStatus.approved,
        ),
        user.username,
        "fac",
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
    user: User = Security(get_user, scopes=["crm_fac_bid"]),
) -> list[BidOutSchema]:
    service.apply_bid_status_filter(
        query,
        "fac_state",
        ApprovalStatus.pending_approval,
        ApprovalStatus.approved,
    )
    return service.get_coordinator_bid_records_at_page(
        page, records_per_page, query, user.username, "fac"
    )


@router.post("/fac/export")
async def export_fac_bids(
    query: QuerySchema, user: User = Security(get_user, scopes=["crm_fac_bid"])
) -> Response:
    service.apply_bid_status_filter(
        query,
        "fac_state",
        ApprovalStatus.pending_approval,
        ApprovalStatus.approved,
    )
    file = service.export_coordintator_bid_records(query, user.username, "fac")

    return StreamingResponse(
        content=file,
        headers={
            "Content-Disposition": "filename=fac_bids.xlsx",
        },
        media_type="application/octet-stream",
    )


@router.patch("/fac/approve/{id}")
async def approve_fac_bid(
    id: int, _: User = Security(get_user, scopes=["crm_fac_bid"])
):
    """Approves bid by `id`"""
    await approve_coordinator_bid(id, "fac_state")


@router.patch("/fac/reject/{id}")
async def reject_fac_bid(
    id: int,
    reason: str,
    _: User = Security(get_user, scopes=["crm_fac_bid"]),
):
    """Rejects bid by `id`"""
    await reject_coordinator_bid(id, reason, "fac_state")


# endregion


# region cc bids
@router.post("/cc/page/info")
async def get_cc_bid_pages_info(
    query: QuerySchema,
    records_per_page: int = 15,
    user: User = Security(get_user, scopes=["crm_cc_bid"]),
) -> TalbeInfoSchema:
    service.apply_bid_status_filter(
        query,
        "cc_state",
        ApprovalStatus.pending_approval,
        ApprovalStatus.approved,
    )
    record_count = service.get_coordinator_bid_count(query, user.username, "cc")
    all_record_count = service.get_coordinator_bid_count(
        service.apply_bid_status_filter(
            QuerySchema(), "cc_state", ApprovalStatus.pending_approval
        ),
        user.username,
        "cc",
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
    user: User = Security(get_user, scopes=["crm_cc_bid"]),
) -> list[BidOutSchema]:
    service.apply_bid_status_filter(
        query,
        "cc_state",
        ApprovalStatus.pending_approval,
        ApprovalStatus.approved,
    )
    return service.get_coordinator_bid_records_at_page(
        page, records_per_page, query, user.username, "cc"
    )


@router.post("/cc/export")
async def export_cc_bids(
    query: QuerySchema, user: User = Security(get_user, scopes=["crm_cc_bid"])
) -> Response:
    service.apply_bid_status_filter(
        query,
        "cc_state",
        ApprovalStatus.pending_approval,
        ApprovalStatus.approved,
    )
    file = service.export_coordintator_bid_records(query, user.username, "cc")

    return StreamingResponse(
        content=file,
        headers={
            "Content-Disposition": "filename=cc_bids.xlsx",
        },
        media_type="application/octet-stream",
    )


@router.patch("/cc/approve/{id}")
async def approve_cc_bid(id: int, _: User = Security(get_user, scopes=["crm_cc_bid"])):
    """Approves bid by `id`"""
    await approve_coordinator_bid(id, "cc_state")


@router.patch("/cc/reject/{id}")
async def reject_cc_bid(
    id: int,
    reason: str,
    _: User = Security(get_user, scopes=["crm_cc_bid"]),
):
    """Rejects bid by `id`"""
    await reject_coordinator_bid(id, reason, "cc_state")


# endregion


# region paralegal bids
@router.post("/paralegal/page/info")
async def get_paralegal_bid_pages_info(
    query: QuerySchema,
    records_per_page: int = 15,
    user: User = Security(get_user, scopes=["crm_paralegal_bid"]),
) -> TalbeInfoSchema:
    service.apply_bid_status_filter(
        query,
        "paralegal_state",
        ApprovalStatus.pending_approval,
        ApprovalStatus.approved,
    )
    record_count = service.get_coordinator_bid_count(query, user.username, "paralegal")
    all_record_count = service.get_coordinator_bid_count(
        service.apply_bid_status_filter(
            QuerySchema(), "paralegal_state", ApprovalStatus.pending_approval
        ),
        user.username,
        "paralegal",
    )
    page_count = (record_count + records_per_page - 1) // records_per_page

    return TalbeInfoSchema(
        record_count=record_count,
        page_count=page_count,
        all_record_count=all_record_count,
    )


@router.post("/paralegal/page/{page}")
async def get_paralegal_bids(
    page: int,
    query: QuerySchema,
    records_per_page: int = 15,
    user: User = Security(get_user, scopes=["crm_paralegal_bid"]),
) -> list[BidOutSchema]:
    service.apply_bid_status_filter(
        query,
        "paralegal_state",
        ApprovalStatus.pending_approval,
        ApprovalStatus.approved,
    )
    return service.get_coordinator_bid_records_at_page(
        page, records_per_page, query, user.username, "paralegal"
    )


@router.post("/paralegal/export")
async def export_paralegal_bids(
    query: QuerySchema,
    user: User = Security(get_user, scopes=["crm_paralegal_bid"]),
) -> Response:
    service.apply_bid_status_filter(
        query,
        "paralegal_state",
        ApprovalStatus.pending_approval,
        ApprovalStatus.approved,
    )
    file = service.export_coordintator_bid_records(query, user.username, "paralegal")

    return StreamingResponse(
        content=file,
        headers={
            "Content-Disposition": "filename=paralegal_bids.xlsx",
        },
        media_type="application/octet-stream",
    )


@router.patch("/paralegal/approve/{id}")
async def approve_paralegal_bid(
    id: int, _: User = Security(get_user, scopes=["crm_paralegal_bid"])
):
    """Approves bid by `id`"""
    await approve_coordinator_bid(id, "paralegal_state")


@router.patch("/paralegal/reject/{id}")
async def reject_paralegal_bid(
    id: int,
    reason: str,
    _: User = Security(get_user, scopes=["crm_paralegal_bid"]),
):
    """Rejects bid by `id`"""
    await reject_coordinator_bid(id, reason, "paralegal")


# endregion cc supervisor bids


# region my bids
@router.post("/my/page/info")
async def get_my_bid_pages_info(
    query: QuerySchema,
    records_per_page: int = 15,
    user: User = Security(get_user, scopes=["authenticated"]),
) -> TalbeInfoSchema:
    service.apply_bid_creator_filter(query, user.username)
    record_count = service.get_bid_count(query)
    all_record_count = service.get_bid_count(
        service.apply_bid_creator_filter(QuerySchema(), user.username)
    )
    page_count = (record_count + records_per_page - 1) // records_per_page

    return TalbeInfoSchema(
        record_count=record_count,
        page_count=page_count,
        all_record_count=all_record_count,
    )


@router.post("/my/page/{page}")
async def get_my_bids(
    page: int,
    query: QuerySchema,
    records_per_page: int = 15,
    user: User = Security(get_user, scopes=["authenticated"]),
) -> list[BidOutSchema]:
    service.apply_bid_creator_filter(query, user.username)
    return service.get_bid_record_at_page(page, records_per_page, query)


@router.post("/my/export")
async def export_my_bids(
    query: QuerySchema,
    user: User = Security(get_user, scopes=["authenticated"]),
) -> Response:
    service.apply_bid_creator_filter(query, user.username)
    file = service.export_bid_records(query)

    return StreamingResponse(
        content=file,
        headers={
            "Content-Disposition": "filename=my_bids.xlsx",
        },
        media_type="application/octet-stream",
    )


# endregion


# region archive bids
@router.post("/archive/page/info")
async def get_archive_bid_pages_info(
    query: QuerySchema,
    records_per_page: int = 15,
    user: User = Security(get_user, scopes=["authenticated"]),
) -> TalbeInfoSchema:
    service.apply_bid_creator_filter(query, user.username)
    service.apply_bid_archive_filter(query)
    record_count = service.get_bid_count(query)
    all_record_count = service.get_bid_count(
        service.apply_bid_archive_filter(
            service.apply_bid_creator_filter(QuerySchema(), user.username)
        )
    )
    page_count = (record_count + records_per_page - 1) // records_per_page

    return TalbeInfoSchema(
        record_count=record_count,
        page_count=page_count,
        all_record_count=all_record_count,
    )


@router.post("/archive/page/{page}")
async def get_archive_bids(
    page: int,
    query: QuerySchema,
    records_per_page: int = 15,
    user: User = Security(get_user, scopes=["authenticated"]),
) -> list[BidOutSchema]:
    service.apply_bid_creator_filter(query, user.username)
    service.apply_bid_archive_filter(query)
    return service.get_bid_record_at_page(page, records_per_page, query)


@router.post("/archive/export")
async def export_archive_bids(
    query: QuerySchema,
    user: User = Security(get_user, scopes=["authenticated"]),
) -> Response:
    service.apply_bid_creator_filter(query, user.username)
    service.apply_bid_archive_filter(query)
    file = service.export_bid_records(query)

    return StreamingResponse(
        content=file,
        headers={
            "Content-Disposition": "filename=my_bids.xlsx",
        },
        media_type="application/octet-stream",
    )


# endregion


async def approve_coordinator_bid(id: int, coordinator_field: str):
    """Approves bid by `id` if coordinator is current coordinator."""
    bid = service.get_bid_by_id(id)

    current_coordinator_field = get_current_coordinator_field(bid)

    if bid and coordinator_field == current_coordinator_field:
        await service.update_bid_state(
            bid, current_coordinator_field, ApprovalStatus.approved
        )


async def reject_coordinator_bid(id: int, reason: str, coordinator_field: str):
    """Rejects bid by `id` if coordinator is current coordinator."""
    bid = service.get_bid_by_id(id)

    current_coordinator_field = get_current_coordinator_field(bid)

    if bid and coordinator_field == current_coordinator_field:
        bid.denying_reason = reason
        await service.update_bid_state(
            bid, current_coordinator_field, ApprovalStatus.denied
        )
