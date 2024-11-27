from fastapi import Response, Security, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter

from app.database.models import ApprovalStatus
from app import services
import app.services.bid as bid_service
from app.database.schemas import BidOutSchema, QuerySchema, TalbeInfoSchema, BidInSchema
from app.adapters.bot.handlers.bids.utils import get_current_coordinator_field

from app.adapters.input.api.auth import User, get_user


router = APIRouter()


# region bids
@router.post("/page/info")
async def get_bid_pages_info(
    query: QuerySchema,
    records_per_page: int = 15,
    _: User = Security(get_user, scopes=["crm_bid|crm_bid_readonly"]),
) -> TalbeInfoSchema:
    record_count = services.get_bid_count(query)
    all_record_count = services.get_bid_count(QuerySchema())
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
    _: User = Security(get_user, scopes=["crm_bid|crm_bid_readonly"]),
) -> list[BidOutSchema]:
    return services.get_bid_record_at_page(page, records_per_page, query)


@router.patch("/approve/{id}")
async def approve_bid(id: int, user: User = Security(get_user, scopes=["crm_bid"])):
    """Approves bid by `id`"""
    bid = services.get_bid_by_id(id)
    if bid:
        coordinator = services.get_worker_by_phone_number(user.username)
        if coordinator is None:
            raise HTTPException(status_code=400, detail="Coordinator not found")
        await services.update_bid_state(
            bid,
            get_current_coordinator_field(bid),
            ApprovalStatus.approved,
            coordinator.id,
        )


@router.patch("/reject/{id}")
async def reject_bid(
    id: int, reason: str, user: User = Security(get_user, scopes=["crm_bid"])
):
    """Rejects bid by `id`"""
    bid = services.get_bid_by_id(id)
    if bid:
        bid.denying_reason = reason
        coordinator = services.get_worker_by_phone_number(user.username)
        if coordinator is None:
            raise HTTPException(status_code=400, detail="Coordinator not found")
        await services.update_bid_state(
            bid,
            get_current_coordinator_field(bid),
            ApprovalStatus.denied,
            coordinator.id,
        )


@router.post("/export")
async def export_bids(
    query: QuerySchema, _: User = Security(get_user, scopes=["crm_bid"])
) -> Response:
    file = services.export_bid_records(query)

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
    services.remove_bid(id)


@router.post("/")
async def create_my_bid(
    bid: BidInSchema,
    user: User = Security(get_user, scopes=["authenticated"]),
) -> BidOutSchema:
    bid.worker = services.get_worker_by_phone_number(user.username)
    return await services.create_bid_by_in_schema(bid)


@router.post("/{id}")
async def add_document(
    id: int,
    files: list[UploadFile],
    _: User = Security(get_user, scopes=["authenticated"]),
):
    services.add_documents_to_bid(id, files)


# endregion


# region fac and cc bids
@router.post("/fac_cc/page/info")
async def get_fac_cc_bid_pages_info(
    query: QuerySchema,
    records_per_page: int = 15,
    user: User = Security(get_user, scopes=["crm_fac_cc_bid"]),
) -> TalbeInfoSchema:
    record_count = bid_services.get_fac_or_cc_bid_count(query, user.username)
    all_record_count = bid_services.get_fac_or_cc_bid_count(
        QuerySchema(),
        user.username,
    )
    page_count = (record_count + records_per_page - 1) // records_per_page
    return TalbeInfoSchema(
        record_count=record_count,
        page_count=page_count,
        all_record_count=all_record_count,
    )


@router.post("/fac_cc/page/{page}")
async def get_fac_cc_bids(
    page: int,
    query: QuerySchema,
    records_per_page: int = 15,
    user: User = Security(get_user, scopes=["crm_fac_cc_bid"]),
) -> list[BidOutSchema]:
    return bid_services.get_fac_or_cc_bid_records_at_page(
        page, records_per_page, query, user.username
    )


@router.post("/fac_cc/export")
async def export_fac_cc_bids(
    query: QuerySchema, user: User = Security(get_user, scopes=["crm_fac_cc_bid"])
) -> Response:
    file = bid_services.export_fac_or_cc_bid_records(query, user.username)

    return StreamingResponse(
        content=file,
        headers={
            "Content-Disposition": "filename=fac_bids.xlsx",
        },
        media_type="application/octet-stream",
    )


@router.patch("/fac_cc/approve/{id}")
async def approve_fac_cc_bid(
    id: int, user: User = Security(get_user, scopes=["crm_fac_cc_bid"])
):
    """Approves bid by `id`"""
    coordinator = services.get_worker_by_phone_number(user.username)
    if coordinator is None:
        raise HTTPException(status_code=400, detail="Coordinator not found")
    await approve_coordinator_bid(id, ["fac_state", "cc_state"], coordinator.id)


@router.patch("/fac_cc/reject/{id}")
async def reject_fac_cc_bid(
    id: int,
    reason: str,
    user: User = Security(get_user, scopes=["crm_fac_cc_bid"]),
):
    """Rejects bid by `id`"""
    coordinator = services.get_worker_by_phone_number(user.username)
    if coordinator is None:
        raise HTTPException(status_code=400, detail="Coordinator not found")
    await reject_coordinator_bid(id, reason, ["fac_state", "cc_state"], coordinator.id)


# history section
@router.post("/fac_cc/history/page/info")
async def get_fac_cc_bid_history_pages_info(
    query: QuerySchema,
    records_per_page: int = 15,
    user: User = Security(get_user, scopes=["crm_fac_cc_bid"]),
) -> TalbeInfoSchema:
    services.apply_bid_status_filter(
        query,
        "fac_state",
        ApprovalStatus.denied,
        ApprovalStatus.approved,
        group=1,
    )
    services.apply_bid_status_filter(
        query,
        "cc_state",
        ApprovalStatus.denied,
        ApprovalStatus.approved,
        group=1,
    )
    record_count = services.get_coordinator_bid_count(
        query, user.username, ["fac", "cc"]
    )
    empty_query = QuerySchema()
    services.apply_bid_status_filter(
        empty_query,
        "fac_state",
        ApprovalStatus.pending_approval,
        group=1,
    )
    services.apply_bid_status_filter(
        empty_query,
        "cc_state",
        ApprovalStatus.pending_approval,
        group=1,
    )
    all_record_count = services.get_coordinator_bid_count(
        empty_query,
        user.username,
        ["fac", "cc"],
    )
    page_count = (record_count + records_per_page - 1) // records_per_page

    return TalbeInfoSchema(
        record_count=record_count,
        page_count=page_count,
        all_record_count=all_record_count,
    )


@router.post("/fac_cc/history/page/{page}")
async def get_fac_cc_history_bids(
    page: int,
    query: QuerySchema,
    records_per_page: int = 15,
    user: User = Security(get_user, scopes=["crm_fac_cc_bid"]),
) -> list[BidOutSchema]:
    services.apply_bid_status_filter(
        query,
        "fac_state",
        ApprovalStatus.denied,
        ApprovalStatus.approved,
        group=1,
    )
    services.apply_bid_status_filter(
        query,
        "cc_state",
        ApprovalStatus.denied,
        ApprovalStatus.approved,
        group=1,
    )
    return services.get_coordinator_bid_records_at_page(
        page, records_per_page, query, user.username, ["fac", "cc"]
    )


# endregion


# region paralegal bids
@router.post("/paralegal/page/info")
async def get_paralegal_bid_pages_info(
    query: QuerySchema,
    records_per_page: int = 15,
    user: User = Security(get_user, scopes=["crm_paralegal_bid"]),
) -> TalbeInfoSchema:
    services.apply_bid_status_filter(
        query, "paralegal_state", ApprovalStatus.pending_approval, group=1
    )
    record_count = services.get_coordinator_bid_count(query, user.username, "paralegal")
    all_record_count = services.get_coordinator_bid_count(
        services.apply_bid_status_filter(
            QuerySchema(), "paralegal_state", ApprovalStatus.pending_approval, group=1
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
    services.apply_bid_status_filter(
        query, "paralegal_state", ApprovalStatus.pending_approval, group=1
    )
    return services.get_coordinator_bid_records_at_page(
        page, records_per_page, query, user.username, "paralegal"
    )


@router.post("/paralegal/export")
async def export_paralegal_bids(
    query: QuerySchema,
    user: User = Security(get_user, scopes=["crm_paralegal_bid"]),
) -> Response:
    services.apply_bid_status_filter(
        query, "paralegal_state", ApprovalStatus.pending_approval, group=1
    )
    file = services.export_coordintator_bid_records(query, user.username, "paralegal")

    return StreamingResponse(
        content=file,
        headers={
            "Content-Disposition": "filename=paralegal_bids.xlsx",
        },
        media_type="application/octet-stream",
    )


@router.patch("/paralegal/approve/{id}")
async def approve_paralegal_bid(
    id: int, user: User = Security(get_user, scopes=["crm_paralegal_bid"])
):
    """Approves bid by `id`"""
    coordinator = services.get_worker_by_phone_number(user.username)
    if coordinator is None:
        raise HTTPException(status_code=400, detail="Coordinator not found")
    await approve_coordinator_bid(id, "paralegal_state", coordinator.id)


@router.patch("/paralegal/reject/{id}")
async def reject_paralegal_bid(
    id: int,
    reason: str,
    user: User = Security(get_user, scopes=["crm_paralegal_bid"]),
):
    """Rejects bid by `id`"""
    coordinator = services.get_worker_by_phone_number(user.username)
    if coordinator is None:
        raise HTTPException(status_code=400, detail="Coordinator not found")
    await reject_coordinator_bid(id, reason, "paralegal_state", coordinator.id)


# endregion


# region accountant card bids
@router.post("/accountant_card/page/info")
async def get_accountant_card_bid_pages_info(
    query: QuerySchema,
    records_per_page: int = 15,
    _: User = Security(get_user, scopes=["crm_accountant_card_bid"]),
) -> TalbeInfoSchema:
    services.apply_bid_status_filter(
        query, "accountant_card_state", ApprovalStatus.pending_approval, group=1
    )
    record_count = services.get_bid_count(query)
    all_record_count = services.get_bid_count(
        services.apply_bid_status_filter(
            QuerySchema(),
            "accountant_card_state",
            ApprovalStatus.pending_approval,
            group=1,
        ),
    )
    page_count = (record_count + records_per_page - 1) // records_per_page

    return TalbeInfoSchema(
        record_count=record_count,
        page_count=page_count,
        all_record_count=all_record_count,
    )


@router.post("/accountant_card/page/{page}")
async def get_accountant_card_bids(
    page: int,
    query: QuerySchema,
    records_per_page: int = 15,
    _: User = Security(get_user, scopes=["crm_accountant_card_bid"]),
) -> list[BidOutSchema]:
    services.apply_bid_status_filter(
        query, "accountant_card_state", ApprovalStatus.pending_approval, group=1
    )
    return services.get_bid_record_at_page(page, records_per_page, query)


@router.post("/accountant_card/export")
async def export_accountant_card_bids(
    query: QuerySchema,
    _: User = Security(get_user, scopes=["crm_accountant_card_bid"]),
) -> Response:
    services.apply_bid_status_filter(
        query, "accountant_card_state", ApprovalStatus.pending_approval, group=1
    )
    file = services.export_bid_records(query)

    return StreamingResponse(
        content=file,
        headers={
            "Content-Disposition": "filename=fac_bids.xlsx",
        },
        media_type="application/octet-stream",
    )


@router.patch("/accountant_card/approve/{id}")
async def approve_accountant_card_bid(
    id: int, user: User = Security(get_user, scopes=["crm_accountant_card_bid"])
):
    """Approves bid by `id`"""
    coordinator = services.get_worker_by_phone_number(user.username)
    if coordinator is None:
        raise HTTPException(status_code=400, detail="Coordinator not found")
    await approve_coordinator_bid(id, "accountant_card_state", coordinator.id)


@router.patch("/accountant_card/reject/{id}")
async def reject_accountant_card_bid(
    id: int,
    reason: str,
    user: User = Security(get_user, scopes=["crm_accountant_card_bid"]),
):
    """Rejects bid by `id`"""
    coordinator = services.get_worker_by_phone_number(user.username)
    if coordinator is None:
        raise HTTPException(status_code=400, detail="Coordinator not found")
    await reject_coordinator_bid(id, reason, "accountant_card_state", coordinator.id)


# endregion


# region my bids
@router.post("/my/page/info")
async def get_my_bid_pages_info(
    query: QuerySchema,
    records_per_page: int = 15,
    user: User = Security(get_user, scopes=["authenticated"]),
) -> TalbeInfoSchema:
    services.apply_bid_creator_filter(query, user.username)
    record_count = services.get_bid_count(query)
    all_record_count = services.get_bid_count(
        services.apply_bid_creator_filter(QuerySchema(), user.username)
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
    services.apply_bid_creator_filter(query, user.username)
    return services.get_bid_record_at_page(page, records_per_page, query)


@router.post("/my/export")
async def export_my_bids(
    query: QuerySchema,
    user: User = Security(get_user, scopes=["authenticated"]),
) -> Response:
    services.apply_bid_creator_filter(query, user.username)
    file = services.export_bid_records(query)

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
    services.apply_bid_creator_filter(query, user.username)
    services.apply_bid_archive_filter(query)
    record_count = services.get_bid_count(query)
    all_record_count = services.get_bid_count(
        services.apply_bid_archive_filter(
            services.apply_bid_creator_filter(QuerySchema(), user.username)
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
    services.apply_bid_creator_filter(query, user.username)
    services.apply_bid_archive_filter(query)
    return services.get_bid_record_at_page(page, records_per_page, query)


@router.post("/archive/export")
async def export_archive_bids(
    query: QuerySchema,
    user: User = Security(get_user, scopes=["authenticated"]),
) -> Response:
    services.apply_bid_creator_filter(query, user.username)
    services.apply_bid_archive_filter(query)
    file = services.export_bid_records(query)

    return StreamingResponse(
        content=file,
        headers={
            "Content-Disposition": "filename=my_bids.xlsx",
        },
        media_type="application/octet-stream",
    )


# endregion


async def approve_coordinator_bid(
    id: int, coordinator_field: str | list[str], coordinator_id: int
):
    """Approves bid by `id` if coordinator is current coordinator."""
    bid = services.get_bid_by_id(id)

    if isinstance(coordinator_field, str):
        coordinator_field = [coordinator_field]

    current_coordinator_field = get_current_coordinator_field(bid)

    if bid and current_coordinator_field in coordinator_field:
        await services.update_bid_state(
            bid, current_coordinator_field, ApprovalStatus.approved, coordinator_id
        )


async def reject_coordinator_bid(
    id: int, reason: str, coordinator_field: str, coordinator_id: int
):
    """Rejects bid by `id` if coordinator is current coordinator."""
    bid = services.get_bid_by_id(id)

    current_coordinator_field = get_current_coordinator_field(bid)

    if bid and coordinator_field == current_coordinator_field:
        bid.denying_reason = reason
        await services.update_bid_state(
            bid, current_coordinator_field, ApprovalStatus.denied, coordinator_id
        )
