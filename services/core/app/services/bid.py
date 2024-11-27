from io import BytesIO
from pathlib import Path
from datetime import datetime
from fastapi import UploadFile
from typing import Any, Optional, Tuple

from app.infra.logging import logger

import app.infra.database.orm as orm
from app.infra.database.models import (
    Department,
    ApprovalStatus,
    Bid,
    Expenditure,
    FujiScope,
    Worker,
)
from app.infra.database.schemas import (
    BidOutSchema,
    BidSchema,
    FilterSchema,
    QuerySchema,
    DocumentSchema,
    WorkerSchema,
    aliases,
    BidInSchema,
)


# In right order
states = [
    "fac_state",
    "cc_state",
    "paralegal_state",
    "kru_state",
    "owner_state",
    "accountant_card_state",
    "accountant_cash_state",
    "teller_card_state",
    "teller_cash_state",
]


def get_bid_count(
    query_schema: QuerySchema,
) -> int:
    """Return bid count in bd."""
    return orm.get_model_count(Bid, query_schema)


def get_bid_record_at_page(
    page: int,
    records_per_page: int,
    query_schema: QuerySchema,
) -> list[BidOutSchema]:
    """Return bid records with applied instructions.

    See `QueryBuilder.apply` for more info applied instructions.
    """
    return [
        bid_to_out_bid(bid)
        for bid in orm.get_models(Bid, BidSchema, page, records_per_page, query_schema)
    ]


async def create_bid_by_in_schema(bid_in: BidInSchema):
    """
    Creates an bid wrapped in `BidSchema` by `BidInSchema` and adds it to database.
    Returns created bid in bd as `BidOutSchema`
    """
    bid = BidSchema(
        activity_type=bid_in.activity_type,
        amount=bid_in.amount,
        payment_type=bid_in.payment_type,
        department=bid_in.department,
        expenditure=bid_in.expenditure,
        worker=bid_in.worker,
        purpose=bid_in.purpose,
        create_date=datetime.now(),
        close_date=None,
        comment=bid_in.comment,
        denying_reason=None,
        documents=[],
        fac_state=ApprovalStatus.pending_approval,
        cc_state=ApprovalStatus.pending,
        paralegal_state=ApprovalStatus.pending
        if bid_in.payment_type == "card"
        else ApprovalStatus.skipped,
        kru_state=ApprovalStatus.pending,
        owner_state=ApprovalStatus.skipped
        if int(bid_in.amount) <= 30000
        else ApprovalStatus.pending,
        accountant_card_state=ApprovalStatus.pending
        if bid_in.payment_type == "card"
        else ApprovalStatus.skipped,
        accountant_cash_state=ApprovalStatus.skipped
        if bid_in.payment_type == "card"
        else ApprovalStatus.pending,
        teller_card_state=ApprovalStatus.pending
        if bid_in.payment_type == "card"
        else ApprovalStatus.skipped,
        teller_cash_state=ApprovalStatus.skipped
        if bid_in.payment_type == "card"
        else ApprovalStatus.pending,
        need_edm=bid_in.need_edm,
    )

    skip_repeating_bid_state(bid, "worker_state")

    bid = orm.add_bid(bid)

    await notify_next_coordinator(bid)

    return bid_to_out_bid(bid)


async def create_bid(
    amount: int,
    payment_type: str,
    department: str,
    purpose: str,
    telegram_id: int,
    expenditure: str,
    files: list[UploadFile],
    fac_state: ApprovalStatus,
    cc_state: ApprovalStatus,
    paralegal_state: ApprovalStatus,
    kru_state: ApprovalStatus,
    owner_state: ApprovalStatus,
    accountant_cash_state: ApprovalStatus,
    accountant_card_state: ApprovalStatus,
    teller_cash_state: ApprovalStatus,
    teller_card_state: ApprovalStatus,
    activity_type: str,
    comment: Optional[str] = None,
    need_edm: Optional[bool] = None,
):
    """
    Creates an bid wrapped in `BidSchema` and adds it to database.
    """
    department_inst = orm.find_department_by_column(Department.name, department)

    if not department_inst:
        logger.error(f"Department with name '{department}' not found")
        return

    worker_inst = orm.find_worker_by_column(Worker.telegram_id, telegram_id)

    if not worker_inst:
        logger.error(f"Worker with telegram id '{telegram_id}' not found")
        return

    expenditure_inst = orm.find_expenditure_by_column(Expenditure.name, expenditure)

    if not expenditure_inst:
        logger.error(f"Expenditure with name '{expenditure}' not found")
        return

    cur_date = datetime.now()
    last_bid_id = orm.get_last_bid_id()
    if not last_bid_id:
        last_bid_id = 0

    documents = []
    for index, file in enumerate(files):
        suffix = Path(file.filename).suffix
        filename = f"document_bid_{last_bid_id + 1}_{index + 1}{suffix}"
        file.filename = filename
        documents.append(DocumentSchema(document=file))
    bid = BidSchema(
        amount=amount,
        payment_type=payment_type,
        department=department_inst,
        paying_department=None,
        expenditure=expenditure_inst,
        worker=worker_inst,
        purpose=purpose,
        create_date=cur_date,
        close_date=None,
        comment=comment,
        denying_reason=None,
        paying_comment=None,
        documents=documents,
        fac_state=fac_state,
        cc_state=cc_state,
        kru_state=kru_state,
        paralegal_state=paralegal_state,
        owner_state=owner_state,
        accountant_card_state=accountant_card_state,
        accountant_cash_state=accountant_cash_state,
        teller_card_state=teller_card_state,
        teller_cash_state=teller_cash_state,
        need_edm=need_edm,
        activity_type=activity_type,
    )

    skip_repeating_bid_state(bid, "worker_state")

    orm.add_bid(bid)

    await notify_next_coordinator(bid)


def add_documents_to_bid(id, files: list[UploadFile]):
    """Adds `files` to bid by bid `id`"""
    documents = []
    for index, file in enumerate(files):
        suffix = Path(file.filename).suffix
        filename = f"document_bid_{id}_{index + 1}{suffix}"
        file.filename = filename
        documents.append(DocumentSchema(document=file))
    orm.add_documents_to_bid(id, documents)


def remove_bid(id: int) -> None:
    """Removes bid by `id` if it exist in database."""
    orm.remove_bid(id)


def get_bids_by_worker_telegram_id(id: str) -> list[BidSchema]:
    """
    Returns all bids own to worker with specified telegram id.
    """
    worker = orm.find_worker_by_column(Worker.telegram_id, id)

    if not worker:
        return []

    return orm.get_bids_by_worker(worker)


def get_workers_bids_by_sender_telegram_id(id: str) -> list[BidSchema]:
    """
    Returns all workers bids own to sender with specified telegram id.
    """
    sender = orm.find_worker_by_column(Worker.telegram_id, id)

    if not sender:
        return []

    return orm.get_workers_bids_by_sender(sender)


def get_pending_bids_by_worker_telegram_id(id: str) -> list[BidSchema]:
    """
    Returns all bids own to worker with specified phone number.
    """
    worker = orm.find_worker_by_column(Worker.telegram_id, id)

    if not worker:
        return []

    return orm.get_pending_bids_by_worker(worker)


def get_bid_by_id(id: int) -> BidSchema:
    """
    Returns bid in database by it id.
    """
    return orm.find_bid_by_column(Bid.id, id)


def get_pending_bids_by_column(column: Any) -> list[BidSchema]:
    """
    Returns all bids in database with pending approval state at column.
    """
    return orm.get_specified_pending_bids(column)


def get_pending_bids_for_teller_cash(tg_id: int) -> list[BidSchema]:
    """
    Returns all bids in database with pending approval state at column for teller cash.
    """

    return orm.get_specified_pending_bids_for_teller_cash(tg_id)


def get_pending_bids_for_cc_fac(tg_id) -> list[BidSchema]:
    return orm.get_pending_bids_for_cc_fac(tg_id)


def get_history_bids_by_column(column: Any) -> list[BidSchema]:
    """
    Returns all bids in database past through worker with `column`.
    """
    return orm.get_specified_history_bids(column)


def get_history_bids_for_teller_cash(tg_id: int) -> list[BidSchema]:
    """
    Returns all bids in database with pending approval state at column.
    """
    return orm.get_specified_history_bids_in_department(tg_id)


def get_history_bids_for_cc_fac(tg_id) -> list[BidSchema]:
    return orm.get_history_bids_for_cc_fac(tg_id)


async def update_bid_state(
    bid: BidSchema, state_name: str, state: ApprovalStatus, coordinator_id: int
):
    """
    Updates bid state with `state_name` by specified `state`.
    """
    from app.adapters.bot.handlers.utils import (
        notify_worker_by_telegram_id,
    )

    if state == ApprovalStatus.approved:
        skip_repeating_bid_state(bid, state_name)

    increment_bid_state(bid, state)

    await notify_next_coordinator(bid)

    if state == ApprovalStatus.approved:
        stage = ""
        match state_name:
            case "fac_state":
                stage = "Ваша заявка согласована ЦФО!"
            case "cc_state":
                stage = "Ваша заявка согласована ЦЗ!"
            case "paralegal_state":
                stage = "Ваша заявка согласована ЮК!"
            case "kru_state":
                stage = "Ваша заявка согласована КРУ!"
            case "owner_state":
                stage = "Ваша заявка согласована собственником!"
            case "accountant_card_state":
                stage = "Ваша заявка согласована бухгалтерией!"
            case "accountant_cash_state":
                if bid.paying_department is not None:
                    stage = f"Денежные средства по вашей заявке готовы к выдачи!\nНа производстве {bid.paying_department.name}."
                else:
                    stage = "Денежные средства по вашей заявке готовы к выдачи!"
            case "teller_card_state":
                stage = "Ваш счёт оплачен."
                if bid.paying_comment is not None:
                    stage += f"\nКомментарий: {bid.paying_comment}"
            case "teller_cash_state":
                stage = "Денежные средства выданы."
            case _:
                stage = "Ваша заявка принята!"
        await notify_worker_by_telegram_id(
            bid.worker.telegram_id, f"{stage}\nНомер заявки: {bid.id}."
        )
        bid.close_date = datetime.now()
    elif state == ApprovalStatus.denied:
        await notify_worker_by_telegram_id(
            bid.worker.telegram_id,
            "Ваша заявка отклонена!\nПричина: " + bid.denying_reason,
        )
        bid.close_date = datetime.now()

    orm.update_bid(bid)
    orm.add_coordinator_to_bid(bid.id, coordinator_id)


def increment_bid_state(bid: BidSchema, state: ApprovalStatus):
    pending_approval_found = False

    for state_name in states:
        if getattr(bid, state_name) == ApprovalStatus.pending_approval:
            setattr(bid, state_name, state)
            pending_approval_found = True
            break

    if not pending_approval_found:
        return

    if state == ApprovalStatus.denied:
        for state_name in states:
            if getattr(bid, state_name) == ApprovalStatus.pending:
                setattr(bid, state_name, ApprovalStatus.skipped)
    else:
        for state_name in states:
            if getattr(bid, state_name) == ApprovalStatus.pending:
                setattr(bid, state_name, ApprovalStatus.pending_approval)
                return


async def notify_next_coordinator(bid: BidSchema):
    """Notifies next coordinator with `ApprovalStatus.pending_approval`."""
    from app.adapters.bot.handlers.utils import (
        notify_workers_by_scope,
        notify_workers_in_department_by_scope,
        notify_worker_by_telegram_id,
    )

    message = f"У вас новая заявка!\nНомер заявки: {bid.id}\nЗаявитель: {bid.worker.l_name} {bid.worker.f_name}"

    if (
        bid.fac_state == ApprovalStatus.pending_approval
        and bid.expenditure.fac.telegram_id is not None
    ):
        await notify_worker_by_telegram_id(
            bid.expenditure.fac.telegram_id, message=message
        )
    elif (
        bid.cc_state == ApprovalStatus.pending_approval
        and bid.expenditure.cc.telegram_id is not None
    ):
        await notify_worker_by_telegram_id(
            bid.expenditure.cc.telegram_id, message=message
        )
    elif (
        bid.paralegal_state == ApprovalStatus.pending_approval
        and bid.expenditure.paralegal.telegram_id is not None
    ):
        await notify_worker_by_telegram_id(
            bid.expenditure.paralegal.telegram_id, message=message
        )
    elif bid.kru_state == ApprovalStatus.pending_approval:
        await notify_workers_by_scope(scope=FujiScope.bot_bid_kru, message=message)
    elif bid.owner_state == ApprovalStatus.pending_approval:
        await notify_workers_by_scope(scope=FujiScope.bot_bid_owner, message=message)
    elif bid.accountant_card_state == ApprovalStatus.pending_approval:
        await notify_workers_by_scope(
            scope=FujiScope.bot_bid_accountant_card, message=message
        )
    elif bid.accountant_cash_state == ApprovalStatus.pending_approval:
        await notify_workers_by_scope(
            scope=FujiScope.bot_bid_accountant_cash, message=message
        )
    elif bid.teller_card_state == ApprovalStatus.pending_approval:
        await notify_workers_by_scope(
            scope=FujiScope.bot_bid_teller_card, message=message
        )
    elif bid.teller_cash_state == ApprovalStatus.pending_approval:
        await notify_workers_in_department_by_scope(
            scope=FujiScope.bot_bid_teller_cash,
            department_id=bid.paying_department.id,
            message=message,
        )


def skip_repeating_bid_state(bid: BidSchema, state_name: str):
    """Skips next stages in `bid.expenditure` with current coordinator"""
    expenditure = bid.expenditure
    match state_name:
        case "worker_state":
            if expenditure.fac.id == bid.worker.id:
                bid.fac_state = ApprovalStatus.skipped
            if expenditure.cc.id == bid.worker.id:
                bid.cc_state = ApprovalStatus.skipped
            if expenditure.paralegal.id == bid.worker.id:
                bid.paralegal_state = ApprovalStatus.skipped

            for state_name in states:
                if getattr(bid, state_name) == ApprovalStatus.pending_approval:
                    return
                if getattr(bid, state_name) == ApprovalStatus.pending:
                    setattr(bid, state_name, ApprovalStatus.pending_approval)
                    return

        case "fac_state":
            if expenditure.cc.id == expenditure.fac.id:
                bid.cc_state = (
                    ApprovalStatus.skipped
                    if bid.cc_state != ApprovalStatus.pending_approval
                    else bid.cc_state
                )
            if expenditure.paralegal.id == expenditure.fac.id:
                bid.paralegal_state = (
                    ApprovalStatus.skipped
                    if bid.paralegal_state != ApprovalStatus.pending_approval
                    else bid.paralegal_state
                )

        case "cc_state":
            if expenditure.paralegal.id == expenditure.cc.id:
                bid.paralegal_state = (
                    ApprovalStatus.skipped
                    if bid.paralegal_state != ApprovalStatus.pending_approval
                    else bid.paralegal_state
                )


def update_bid(bid: BidSchema, paying_department_name: Optional[str] = None):
    """Updated bid in database by `bid`"""
    orm.update_bid(bid, paying_department_name)


def bid_to_out_bid(bid: BidSchema) -> BidOutSchema:
    """Converts `BidSchema` to `BidRecordSchema`"""
    from app.adapters.bot.handlers.bids.utils import get_bid_state_info

    return BidOutSchema(
        id=bid.id,
        amount=bid.amount,
        payment_type=bid.payment_type,
        department=bid.department,
        worker=bid.worker,
        close_date=bid.close_date,
        need_edm=bid.need_edm,
        comment=bid.comment,
        create_date=bid.create_date,
        documents=[doc.document for doc in bid.documents],
        purpose=bid.purpose,
        status=get_bid_state_info(bid, "/next/"),
        denying_reason=bid.denying_reason,
        expenditure=bid.expenditure,
        activity_type=bid.activity_type,
    )


def get_bid_records() -> list[BidOutSchema]:
    """Returns all bid records in database."""
    return [bid_to_out_bid(bid) for bid in orm.get_bids()]


def apply_coordinator_filter(
    query_schema: QuerySchema, phone: int, coordinator: str | list[str], group: int = 0
) -> None:
    if isinstance(coordinator, str):
        coordinator = [coordinator]

    for val in coordinator:
        query_schema.filter_query.append(
            FilterSchema(
                column="expenditure",
                value="",
                dependencies=[
                    FilterSchema(
                        column=val,
                        value="",
                        dependencies=[FilterSchema(column="phone_number", value=phone)],
                    )
                ],
                groups=[group],
            ),
        )


def get_coordinator_bid_records_at_page(
    page: int,
    records_per_page: int,
    query_schema: QuerySchema,
    phone: int,
    coordinator: str | list[str],
    group: int = 0,
) -> list[BidOutSchema]:
    """Returns all coordinator bid records in database."""
    apply_coordinator_filter(query_schema, phone, coordinator, group)

    return get_bid_record_at_page(page, records_per_page, query_schema)


def get_coordinator_bid_count(
    query_schema: QuerySchema, phone: int, coordinator: str | list[str], group: int = 0
) -> int:
    """Returns all coordinator bid records in database."""
    apply_coordinator_filter(query_schema, phone, coordinator, group)

    return get_bid_count(query_schema)


def apply_bid_status_filter(
    query_schema: QuerySchema,
    status_field: str,
    *statuses: ApprovalStatus,
    group: int = 0,
) -> QuerySchema:
    """Apply filter query by bid status to bid query. Return query with applied filter."""
    for status in statuses:
        query_schema.filter_query.append(
            FilterSchema(column=status_field, value=status, groups=[group]),
        )
    return query_schema


def apply_bid_creator_filter(
    query_schema: QuerySchema, creator_phone: str
) -> QuerySchema:
    """Apply filter query by bid creator to bid query. Return query with applied filter."""
    query_schema.filter_query.append(
        FilterSchema(
            column="worker",
            value="",
            dependencies=[FilterSchema(column="phone_number", value=creator_phone)],
        ),
    )
    return query_schema


def apply_bid_archive_filter(query_schema: QuerySchema) -> QuerySchema:
    """Apply filter query by bid denied or approved status to bid query.
    Return query with applied filter."""
    query_schema.filter_query.extend(
        [
            FilterSchema(column="fac_state", value=ApprovalStatus.denied, groups=[0]),
            FilterSchema(column="cc_state", value=ApprovalStatus.denied, groups=[0]),
            FilterSchema(
                column="paralegal_state", value=ApprovalStatus.denied, groups=[0]
            ),
            FilterSchema(column="kru_state", value=ApprovalStatus.denied, groups=[0]),
            FilterSchema(column="owner_state", value=ApprovalStatus.denied, groups=[0]),
            FilterSchema(
                column="accountant_card_state", value=ApprovalStatus.denied, groups=[0]
            ),
            FilterSchema(
                column="accountant_cash_state", value=ApprovalStatus.denied, groups=[0]
            ),
            FilterSchema(
                column="teller_card_state", value=ApprovalStatus.denied, groups=[0]
            ),
            FilterSchema(
                column="teller_card_state", value=ApprovalStatus.approved, groups=[0]
            ),
            FilterSchema(
                column="teller_cash_state", value=ApprovalStatus.denied, groups=[0]
            ),
            FilterSchema(
                column="teller_cash_state", value=ApprovalStatus.approved, groups=[0]
            ),
        ]
    )
    return query_schema


def export_bid_records(
    query_schema: QuerySchema,
) -> BytesIO:
    """Returns xlsx file with bids records filtered by `query_schema`."""
    # Formatters
    from app.adapters.bot.kb import payment_type_dict

    return orm.export_models(
        Bid,
        query_schema,
        dict(
            payment_type=lambda type: payment_type_dict[type],
            need_edm=lambda need: "Да" if need else "Нет",
        ),
        [
            "documents",
            "fac_state",
            "cc_state",
            "paralegal_state",
            "kru_state",
            "owner_state",
            "accountant_card_state",
            "accountant_cash_state",
            "teller_card_state",
            "teller_cash_state",
        ],
        aliases[BidSchema],
    )


def export_coordintator_bid_records(
    query_schema: QuerySchema,
    phone: int,
    coordinator: str | list[str],
    group: int = 0,
) -> BytesIO:
    """Returns xlsx file with bids records filtered by `query_schema`
    for specified `coordinator`."""
    apply_coordinator_filter(query_schema, phone, coordinator, group)

    return export_bid_records(query_schema)


def get_bid_coordinators(bid_id: int) -> list[WorkerSchema]:
    """Returns coordinators for specified `bid_id`"""
    return orm.get_bid_coordinators(bid_id)


def get_fac_or_cc_bid_count(query_schema: QuerySchema, worker_phone: str) -> int:
    """Return bid count in bd."""
    bids_select = orm.create_fac_or_cc_select_query(worker_phone)
    return orm.get_model_count(Bid, query_schema, bids_select)


def get_fac_or_cc_bid_records_at_page(
    page: int, records_per_page: int, query_schema: QuerySchema, worker_phone: str
) -> list[BidOutSchema]:
    """Return bid records with applied instructions.

    See `QueryBuilder.apply` for more info applied instructions.
    """
    bids_select = orm.create_fac_or_cc_select_query(worker_phone)
    return [
        bid_to_out_bid(bid)
        for bid in orm.get_models(
            Bid, BidSchema, page, records_per_page, query_schema, bids_select
        )
    ]


def export_fac_or_cc_bid_records(
    query_schema: QuerySchema, worker_phone: str
) -> BytesIO:
    """Returns xlsx file with bids records filtered by `query_schema`."""
    # Formatters
    from app.adapters.bot.kb import payment_type_dict

    bids_select = orm.create_fac_or_cc_select_query(worker_phone)

    return orm.export_models(
        Bid,
        query_schema,
        dict(
            payment_type=lambda type: payment_type_dict[type],
            need_edm=lambda need: "Да" if need else "Нет",
        ),
        [
            "documents",
            "fac_state",
            "cc_state",
            "paralegal_state",
            "kru_state",
            "owner_state",
            "accountant_card_state",
            "accountant_cash_state",
            "teller_card_state",
            "teller_cash_state",
        ],
        aliases[BidSchema],
        select_query=bids_select,
    )


def find_bid_for_worker(bid_id: int, tg_id: int) -> Tuple[BidSchema, bool] | None:
    """Find bid by id and telegram id

    :Return: bid and worker access state for this bid, if bid found, `None` otherwise
    """
    bid = orm.find_bid_by_column(Bid.id, bid_id)
    if bid is None:
        return None
    try:
        worker = orm.get_workers_with_post_by_column(Worker.telegram_id, tg_id)[0]
    except IndexError:
        logger.error(f"Worker with telegram id: {tg_id} not found")
    if FujiScope.admin in worker.post.scopes:
        return (bid, True)

    if FujiScope.bot_bid_fac_cc in worker.post.scopes:  #    FujiScope.bot_bid_fac_cc
        for state in [["fac_state", "fac"], ["cc_state", "cc"]]:
            if (
                getattr(bid, state[0]) != ApprovalStatus.skipped
                and worker.id == getattr(bid.expenditure, state[1]).id
            ):
                return (bid, True)

    for scope, state in {
        FujiScope.bot_bid_kru: "kru_state",
        FujiScope.bot_bid_owner: "owner_state",
        FujiScope.bot_bid_accountant_card: "accountant_card_state",
        FujiScope.bot_bid_accountant_cash: "accountant_cash_state",
        FujiScope.bot_bid_teller_card: "teller_card_state",
    }.items():
        if (
            getattr(bid, state) != ApprovalStatus.skipped
            and scope in worker.post.scopes
        ):
            return (bid, True)

    if (
        FujiScope.bot_bid_teller_cash in worker.post.scopes
        and bid.paying_department is not None
        and bid.paying_department.id == worker.department.id
        and bid.teller_cash_state != ApprovalStatus.skipped
    ):  #        FujiScope.bot_bid_teller_cash
        return (bid, True)

    if worker.id == bid.worker.id:  #    FujiScope.bot_bid_create
        return (bid, True)
    return (bid, False)
