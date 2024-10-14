from datetime import datetime
from io import BytesIO
from typing import Any, Callable, Optional, Type
from db.query import QueryBuilder, XLSXExporter
from db.database import Base, engine, session
from db.models import (
    Bid,
    BidDocument,
    BudgetRecord,
    Executor,
    Expenditure,
    FujiScope,
    Group,
    Post,
    PostScope,
    TechnicalProblem,
    TechnicalRequest,
    TechnicalRequestProblemPhoto,
    TechnicalRequestRepairPhoto,
    WorkTime,
    Worker,
    Department,
    ApprovalStatus,
    WorkerBid,
    WorkerBidWorksheet,
    WorkerBidPassport,
    WorkerBidWorkPermission,
    ProblemIT,
    BidIT,
    BidITWorkerDocument,
    BidITRepairmanDocument,
    AccountLogins,
    Subordination,
    MaterialValues,
)
from db.schemas import (
    BaseSchema,
    BidSchema,
    BudgetRecordSchema,
    DepartmentSchema,
    DocumentSchema,
    ExpenditureSchema,
    GroupSchema,
    QuerySchema,
    TechnicalProblemSchema,
    TechnicalRequestSchema,
    WorkerBidSchema,
    WorkerSchema,
    WorkTimeSchema,
    PostSchema,
    ProblemITSchema,
    BidITSchema,
    AccountLoginsSchema,
    MaterialValuesSchema,
)
from pydantic import BaseModel
from sqlalchemy.sql.expression import func
from sqlalchemy import null, or_, and_, desc


def create_tables():
    Base.metadata.create_all(engine)


def find_worker_by_column(column: any, value: any) -> WorkerSchema:
    """
    Returns worker in database by `column` with `value`.
    If worker not exist return `None`.
    """
    with session.begin() as s:
        raw_worker = s.query(Worker).filter(column == value).first()
        if not raw_worker:
            return None
        return WorkerSchema.model_validate(raw_worker)


def find_workers_by_name(name: str) -> list[WorkerSchema]:
    """
    Returns workers in database by given `name`.
    Fields for search: `Worker.f_name`, `Worker.l_name`, `Worker.o_name`

    Search is equivalent sql like statement.
    """
    with session.begin() as s:
        raw_workers = s.query(Worker).filter(
            or_(
                Worker.f_name.ilike(f"%{name}%"),
                Worker.l_name.ilike(f"%{name}%"),
                Worker.o_name.ilike(f"%{name}%"),
            )
        )
        return [WorkerSchema.model_validate(raw_worker) for raw_worker in raw_workers]


def find_posts_by_name(name: str) -> list[PostSchema]:
    """
    Returns posts in database by given `name`.
    Fields for search: `Post.name`

    Search is equivalent sql like statement.
    """
    with session.begin() as s:
        raw_posts = s.query(Post).filter(
            or_(
                Post.name.ilike(f"%{name}%"),
            )
        )
        return [PostSchema.model_validate(raw_post) for raw_post in raw_posts]


def find_department_by_column(column: any, value: any) -> DepartmentSchema:
    """
    Returns department in database by `column` with `value`.
    If department not exist return `None`.
    """
    with session.begin() as s:
        raw_department = s.query(Department).filter(column == value).first()
        if not raw_department:
            return None
        return DepartmentSchema.model_validate(raw_department)


def find_post_by_column(column: any, value: any) -> PostSchema:
    """
    Returns post in database by `column` with `value`.
    If post not exist return `None`.
    """
    with session.begin() as s:
        raw_post = s.query(Post).filter(column == value).first()
        if not raw_post:
            return None
        return PostSchema.model_validate(raw_post)


def find_bid_by_column(column: any, value: any) -> BidSchema:
    """
    Returns bid in database by `column` with `value`.
    If bid not exist return `None`.
    """
    with session.begin() as s:
        raw_bid = s.query(Bid).filter(column == value).first()
        if not raw_bid:
            return None
        return BidSchema.model_validate(raw_bid)


def find_worker_bid_by_column(column: any, value: any) -> WorkerBidSchema:
    """
    Returns worker bid in database by `column` with `value`.
    If worker bid not exist return `None`.
    """
    with session.begin() as s:
        raw_bid = s.query(WorkerBid).filter(column == value).first()
        if not raw_bid:
            return None
        return WorkerBidSchema.model_validate(raw_bid)


def update_worker(worker: WorkerSchema):
    """Updates worker by his id."""
    with session.begin() as s:
        cur_worker = s.query(Worker).filter(Worker.id == worker.id).first()
        if not cur_worker:
            return None
        cur_worker.b_date = worker.b_date
        cur_worker.f_name = worker.f_name
        cur_worker.l_name = worker.l_name
        cur_worker.o_name = worker.o_name
        cur_worker.phone_number = worker.phone_number
        cur_worker.telegram_id = worker.telegram_id


def get_departments_columns(*columns: list[Any]) -> list[DepartmentSchema]:
    """
    Returns specified columns of all existed departments.
    """
    with session.begin() as s:
        return s.query(Department).with_entities(*columns).all()


def get_last_bid_id() -> int:
    """
    Returns last bid id in database.
    """
    with session.begin() as s:
        return s.query(func.max(Bid.id)).first()[0]


def get_last_worker_bid_id() -> int:
    """
    Returns last worker bid id in database.
    """
    with session.begin() as s:
        return s.query(func.max(WorkerBid.id)).first()[0]


def add_documents_to_bid(id, documents: DocumentSchema):
    with session.begin() as s:
        bid = s.query(Bid).filter(Bid.id == id).first()

        for document in documents:
            s.add(BidDocument(bid=bid, document=document.document))


def add_bid(bid: BidSchema) -> BidSchema:
    """
    Adds `bid` to database.
    """
    with session.begin() as s:
        worker = s.query(Worker).filter(Worker.id == bid.worker.id).first()
        department = (
            s.query(Department).filter(Department.id == bid.department.id).first()
        )
        expenditure = (
            s.query(Expenditure).filter(Expenditure.id == bid.expenditure.id).first()
        )

        bid_model = Bid(
            amount=bid.amount,
            payment_type=bid.payment_type,
            purpose=bid.purpose,
            comment=bid.comment,
            create_date=bid.create_date,
            department=department,
            worker=worker,
            documents=[],
            paralegal_state=bid.paralegal_state,
            owner_state=bid.owner_state,
            accountant_card_state=bid.accountant_card_state,
            accountant_cash_state=bid.accountant_cash_state,
            teller_card_state=bid.teller_card_state,
            teller_cash_state=bid.teller_cash_state,
            fac_state=bid.fac_state,
            cc_state=bid.cc_state,
            kru_state=bid.kru_state,
            expenditure=expenditure,
            need_edm=bid.need_edm,
        )
        s.add(bid_model)

        for document in bid.documents:
            s.add(BidDocument(bid=bid_model, document=document.document))
        s.flush()
        s.refresh(bid_model)

        bid.id = bid_model.id

        return bid


def get_bids_by_worker(worker: WorkerSchema) -> list[BidSchema]:
    """
    Returns all bids in database by worker.
    """
    with session.begin() as s:
        raw_bids = s.query(Bid).filter(Bid.worker_id == worker.id).all()
        return [BidSchema.model_validate(raw_bid) for raw_bid in raw_bids]


def get_workers_bids_by_sender(sender: WorkerSchema) -> list[BidSchema]:
    """
    Returns all bids in database by worker.
    """
    with session.begin() as s:
        raw_bids = s.query(WorkerBid).filter(WorkerBid.sender_id == sender.id).all()
        return [WorkerBidSchema.model_validate(raw_bid) for raw_bid in raw_bids]


def get_pending_bids_by_worker(worker: WorkerSchema) -> list[BidSchema]:
    """
    Returns all bids in database by worker.
    """
    with session.begin() as s:
        raw_bids = (
            s.query(Bid)
            .filter(
                and_(
                    Bid.worker_id == worker.id,
                    or_(
                        Bid.fac_state == ApprovalStatus.pending_approval,
                        Bid.cc_state == ApprovalStatus.pending_approval,
                        Bid.kru_state == ApprovalStatus.pending_approval,
                        Bid.accountant_card_state == ApprovalStatus.pending_approval,
                        Bid.accountant_cash_state == ApprovalStatus.pending_approval,
                        Bid.teller_card_state == ApprovalStatus.pending_approval,
                        Bid.teller_cash_state == ApprovalStatus.pending_approval,
                        Bid.paralegal_state == ApprovalStatus.pending_approval,
                        Bid.owner_state == ApprovalStatus.pending_approval,
                    ),
                )
            )
            .all()
        )
        return [BidSchema.model_validate(raw_bid) for raw_bid in raw_bids]


def get_specified_pengind_bids(pending_column) -> list[BidSchema]:
    """
    Returns all bids in database with
    pending approval state in `pending_column`.
    """
    with session.begin() as s:
        raw_bids = (
            s.query(Bid).filter(pending_column == ApprovalStatus.pending_approval).all()
        )
        return [BidSchema.model_validate(raw_bid) for raw_bid in raw_bids]


def get_specified_history_bids(pending_column) -> list[BidSchema]:
    """
    Returns all bids in database with approval or
    denied state in `pending_column`.
    """
    with session.begin() as s:
        raw_bids = (
            s.query(Bid)
            .filter(
                or_(
                    pending_column == ApprovalStatus.denied,
                    pending_column == ApprovalStatus.approved,
                )
            )
            .all()
        )
        return [BidSchema.model_validate(raw_bid) for raw_bid in raw_bids]


def update_bid(bid: BidSchema):
    """Updates bid by it id."""
    with session.begin() as s:
        cur_bid = s.query(Bid).filter(Bid.id == bid.id).first()
        if not cur_bid:
            return None

        new_worker = s.query(Worker).filter(Worker.id == bid.worker.id).first()
        if not new_worker:
            return None

        new_department = (
            s.query(Department).filter(Department.id == bid.department.id).first()
        )
        if not new_worker:
            return None

        new_expenditure = (
            s.query(Expenditure).filter(Expenditure.id == bid.expenditure.id).first()
        )
        if not new_expenditure:
            return None

        cur_bid.amount = bid.amount
        cur_bid.payment_type = bid.payment_type
        cur_bid.purpose = bid.purpose
        cur_bid.comment = bid.comment
        cur_bid.denying_reason = bid.denying_reason
        cur_bid.create_date = bid.create_date
        cur_bid.close_date = bid.close_date
        cur_bid.department = new_department
        cur_bid.worker = new_worker
        cur_bid.expenditure = new_expenditure
        # TODO: Update documents
        # cur_bid.document = bid.document
        # cur_bid.document1 = bid.document1
        # cur_bid.document2 = bid.document2
        cur_bid.paralegal_state = bid.paralegal_state
        cur_bid.owner_state = bid.owner_state
        cur_bid.accountant_card_state = bid.accountant_card_state
        cur_bid.accountant_cash_state = bid.accountant_cash_state
        cur_bid.teller_card_state = bid.teller_card_state
        cur_bid.teller_cash_state = bid.teller_cash_state
        cur_bid.fac_state = bid.fac_state
        cur_bid.cc_state = bid.cc_state
        cur_bid.kru_state = bid.kru_state
        cur_bid.need_edm = bid.need_edm


def get_workers_with_post_by_column(column: Any, value: Any) -> list[WorkerSchema]:
    """
    Returns all `Worker` as `WorkerSchema` in database
    by `column` with `value`.

    Using `get_workers_with_post_by_columns`.
    """
    return get_workers_with_post_by_columns([column], [value])


def get_workers_with_post_by_columns(
    columns: list[Any], values: list[Any]
) -> list[WorkerSchema]:
    """
    Returns all `Worker` as `WorkerSchema` in database
    by `columns` with `values`.
    """
    with session.begin() as s:
        query = s.query(Worker).join(Worker.post)
        for column, value in zip(columns, values):
            query = query.filter(column == value)
        raw_models = query.all()
        return [WorkerSchema.model_validate(raw_model) for raw_model in raw_models]


def get_workers_with_scope(scope: FujiScope) -> list[WorkerSchema]:
    """
    Returns all `Worker` as `WorkerSchema` in database
    by `scope`.
    """
    with session.begin() as s:
        raw_models = (
            s.query(Worker)
            .join(Worker.post)
            .join(Post.scopes)
            .filter(PostScope.scope == scope)
        ).all()
        return [WorkerSchema.model_validate(raw_model) for raw_model in raw_models]


def get_work_time_records_by_columns(
    columns: list[Any], values: list[Any], limit: int = None
) -> list[WorkTimeSchema]:
    """
    Returns all `WorkTime` as `WorkTimeSchema` in database
    by `columns` with `values`.
    """
    with session.begin() as s:
        query = s.query(WorkTime)
        for column, value in zip(columns, values):
            query = query.filter(column == value)

        if limit:
            query = query.limit(limit)

        raw_models = query.all()
        return [WorkTimeSchema.model_validate(raw_model) for raw_model in raw_models]


def find_work_time_record_by_columns(
    columns: list[Any], values: list[Any]
) -> WorkTimeSchema:
    """
    Returns `WorkTime` as `WorkTimeSchema` in database
    by `columns` with `values`.

    If record not exist return `None`.
    """
    with session.begin() as s:
        query = s.query(WorkTime)
        for column, value in zip(columns, values):
            query = query.filter(column == value)

        raw_model = query.first()

        if not raw_model:
            return None

        return WorkTimeSchema.model_validate(raw_model)


def update_work_time(record: WorkTimeSchema):
    """Updates work time by it id."""
    with session.begin() as s:
        old = s.query(WorkTime).filter(WorkTime.id == record.id).first()

        if not record:
            return None

        if record.worker:
            worker = s.query(Worker).filter(Worker.id == record.worker.id).first()
            old.worker = worker

        if record.department:
            department = (
                s.query(Department)
                .filter(Department.id == record.department.id)
                .first()
            )
            old.department = department

        old.day = record.day
        old.work_begin = record.work_begin
        old.work_end = record.work_end
        old.work_duration = record.work_duration
        old.rating = record.rating
        old.fine = record.fine


def get_posts() -> list[PostSchema]:
    """Returns all posts in database."""
    with session.begin() as s:
        raw_models = s.query(Post).all()
        return [PostSchema.model_validate(raw_model) for raw_model in raw_models]


def add_worker_bid(bid: WorkerBidSchema):
    """
    Adds `bid` to database.
    """
    with session.begin() as s:
        department = (
            s.query(Department).filter(Department.id == bid.department.id).first()
        )
        post = s.query(Post).filter(Post.id == bid.post.id).first()
        sender = s.query(Worker).filter(Worker.id == bid.sender.id).first()

        worker_bid = WorkerBid(
            f_name=bid.f_name,
            l_name=bid.l_name,
            o_name=bid.o_name,
            post=post,
            department=department,
            state=bid.state,
            create_date=bid.create_date,
            sender=sender,
        )

        s.add(worker_bid)

        for doc in bid.worksheet:
            file = WorkerBidWorksheet(worker_bid=worker_bid, document=doc.document)
            s.add(file)

        for doc in bid.passport:
            file = WorkerBidPassport(worker_bid=worker_bid, document=doc.document)
            s.add(file)

        for doc in bid.work_permission:
            file = WorkerBidWorkPermission(worker_bid=worker_bid, document=doc.document)
            s.add(file)


def update_worker_bid(bid: WorkerBidSchema):
    """Updates worker bid by it id."""
    with session.begin() as s:
        cur_bid = s.query(WorkerBid).filter(WorkerBid.id == bid.id).first()
        if not cur_bid:
            return

        new_post = s.query(Post).filter(Post.id == bid.post.id).first()
        if not new_post:
            return

        sender = s.query(Worker).filter(Worker.id == bid.sender.id).first()
        if not sender:
            return None

        new_department = (
            s.query(Department).filter(Department.id == bid.department.id).first()
        )
        if not new_department:
            return

        cur_bid.create_date = bid.create_date
        cur_bid.department = new_department
        cur_bid.post = new_post
        # TODO: Update documents
        cur_bid.state = bid.state
        cur_bid.f_name = bid.f_name
        cur_bid.l_name = bid.l_name
        cur_bid.o_name = bid.o_name
        cur_bid.sender = sender


def get_expenditures() -> list[ExpenditureSchema]:
    """Returns all expenditures in database."""
    with session.begin() as s:
        raw_models = s.query(Expenditure).all()
        return [ExpenditureSchema.model_validate(raw_model) for raw_model in raw_models]


def create_expenditure(expenditure: ExpenditureSchema) -> bool:
    """Creates expenditure
    Returns: `True` if expenditure created, `False` otherwise.
    """
    with session.begin() as s:
        fac = s.query(Worker).filter(Worker.id == expenditure.fac.id).first()
        cc = s.query(Worker).filter(Worker.id == expenditure.cc.id).first()
        kru = s.query(Worker).filter(Worker.id == expenditure.kru.id).first()
        creator = s.query(Worker).filter(Worker.id == expenditure.creator.id).first()

        if not cc or not fac or not kru or not creator:
            return False

        expenditure_model = Expenditure(
            name=expenditure.name,
            chapter=expenditure.chapter,
            create_date=expenditure.create_date,
            fac=fac,
            cc=cc,
            kru=kru,
            creator=creator,
        )

        s.add(expenditure_model)

    return True


def remove_expenditure(id: int) -> None:
    """Removes expenditure"""
    with session.begin() as s:
        expenditure = s.query(Expenditure).filter(Expenditure.id == id).first()
        if expenditure:
            s.delete(expenditure)


def update_expenditure(expenditure: ExpenditureSchema) -> bool:
    """Updates expenditure
    Returns: `True` if expenditure updated, `False` otherwise.
    """
    with session.begin() as s:
        old = s.query(Expenditure).filter(Expenditure.id == expenditure.id).first()

        fac = s.query(Worker).filter(Worker.id == expenditure.fac.id).first()
        cc = s.query(Worker).filter(Worker.id == expenditure.cc.id).first()
        kru = s.query(Worker).filter(Worker.id == expenditure.kru.id).first()

        if not old or not cc or not fac or not kru:
            return False

        old.name = expenditure.name
        old.chapter = expenditure.chapter
        old.create_date = expenditure.create_date
        old.fac = fac
        old.cc = cc
        old.kru = kru

    return True


def find_expenditure_by_column(column: any, value: any) -> ExpenditureSchema:
    """
    Returns updated expenditure in database by `column` with `value`.
    If updated expenditure not exist return `None`.
    """
    with session.begin() as s:
        raw_expenditure = s.query(Expenditure).filter(column == value).first()
        if not raw_expenditure:
            return None
        return ExpenditureSchema.model_validate(raw_expenditure)


def get_last_expenditrure() -> ExpenditureSchema:
    """Returns last expenditure bind db."""
    with session.begin() as s:
        raw_expenditure = s.query(Expenditure).order_by(desc(Expenditure.id)).first()
        if not raw_expenditure:
            return None
        return ExpenditureSchema.model_validate(raw_expenditure)


def get_budget_records() -> list[BudgetRecordSchema]:
    """Returns all budget records in database."""
    with session.begin() as s:
        raw_models = s.query(BudgetRecord).all()
        return [
            BudgetRecordSchema.model_validate(raw_model) for raw_model in raw_models
        ]


def remove_budget_record(id: int) -> None:
    """Removes budget_record"""
    with session.begin() as s:
        s.query(BudgetRecord).filter(BudgetRecord.id == id).delete()


def create_budget_record(record: BudgetRecordSchema) -> bool:
    """Creates budget record
    Returns: `True` if budget record created, `False` otherwise.
    """
    with session.begin() as s:
        expenditure = (
            s.query(Expenditure).filter(Expenditure.id == record.expenditure.id).first()
        )

        department = None
        if record.department:
            department = (
                s.query(Department)
                .filter(Department.id == record.department.id)
                .first()
            )

        if not expenditure or (record.department and not department):
            return False

        record_model = BudgetRecord(
            expenditure=expenditure,
            limit=record.limit,
            department=department,
            last_update=record.last_update,
        )

        s.add(record_model)

    return True


def get_last_budget_record() -> BudgetRecordSchema:
    """Returns last budget record bind db."""
    with session.begin() as s:
        raw_expenditure = s.query(BudgetRecord).order_by(desc(BudgetRecord.id)).first()
        if not raw_expenditure:
            return None
        return BudgetRecordSchema.model_validate(raw_expenditure)


def update_budget_record(record: BudgetRecordSchema) -> bool:
    """Updates budget record
    Returns: `True` if budget record updated, `False` otherwise.
    """
    with session.begin() as s:
        old = s.query(BudgetRecord).filter(BudgetRecord.id == record.id).first()

        expenditure = (
            s.query(Expenditure).filter(Expenditure.id == record.expenditure.id).first()
        )
        department = None
        if record.department:
            department = (
                s.query(Department)
                .filter(Department.id == record.department.id)
                .first()
            )

        if not old or not expenditure:
            return False

        old.expenditure = expenditure
        old.limit = record.limit
        old.department = department
        old.last_update = record.last_update

    return True


def find_budget_record_by_column(column: any, value: any) -> BudgetRecordSchema:
    """
    Returns updated budget record in database by `column` with `value`.
    If updated budget record not exist return `None`.
    """
    with session.begin() as s:
        raw_budget_record = s.query(BudgetRecord).filter(column == value).first()
        if not raw_budget_record:
            return None
        return BudgetRecordSchema.model_validate(raw_budget_record)


def find_expenditures_by_name(name: str) -> list[ExpenditureSchema]:
    """
    Returns expenditures in database by given `name`.
    Fields for search: `Expenditure.name`, `Expenditure.chapter`

    Search is equivalent sql like statement.
    """
    with session.begin() as s:
        raw_expenditures = s.query(Expenditure).filter(
            or_(
                Expenditure.name.ilike(f"%{name}%"),
                Expenditure.chapter.ilike(f"%{name}%"),
            )
        )
        return [
            ExpenditureSchema.model_validate(raw_expenditure)
            for raw_expenditure in raw_expenditures
        ]


def find_departments_by_name(name: str) -> list[DepartmentSchema]:
    """
    Returns departments in database by given `name`.
    Fields for search: `Department.name`

    Search is equivalent sql like statement.
    """
    with session.begin() as s:
        raw_departments = s.query(Department).filter(
            or_(
                Department.name.ilike(f"%{name}%"),
            )
        )
        return [
            DepartmentSchema.model_validate(raw_department)
            for raw_department in raw_departments
        ]


def get_bids() -> list[BidSchema]:
    """Returns all bids in database."""
    with session.begin() as s:
        raw_models = s.query(Bid).all()
        return [BidSchema.model_validate(raw_model) for raw_model in raw_models]


def get_groups() -> list[GroupSchema]:
    """Returns all groups in database."""
    with session.begin() as s:
        raw_models = s.query(Group).all()
        return [GroupSchema.model_validate(raw_model) for raw_model in raw_models]


def remove_bid(id: int) -> None:
    """Removes bid by `id` if it exist in db."""
    with session.begin() as s:
        if bid := s.query(Bid).filter(Bid.id == id).first():
            s.delete(bid)


def get_group_by_name(name: str) -> GroupSchema:
    """Returns GroupSchema by name"""
    with session.begin() as s:
        raw_model = s.query(Group).filter(Group.name == name).first()
        return GroupSchema.model_validate(raw_model)


def get_all_worker_in_group(group_id: int) -> list[WorkerSchema]:
    """Return all workers in group"""
    with session.begin() as s:
        raw_models = s.query(Worker).filter(Worker.group_id == group_id)
        return [WorkerSchema.model_validate(raw_model) for raw_model in raw_models]


# region Technical problem


def get_technical_problems() -> list[TechnicalProblemSchema]:
    """Returns list of ProblemSchema"""
    with session.begin() as s:
        raw_models = s.query(TechnicalProblem).all()
        return [
            TechnicalProblemSchema.model_validate(raw_model) for raw_model in raw_models
        ]


def get_technical_problem_by_id(problem_id: int) -> TechnicalProblemSchema:
    with session.begin() as s:
        return TechnicalProblemSchema.model_validate(
            s.query(TechnicalProblem).filter(TechnicalProblem.id == problem_id).first()
        )


def get_technical_problem_by_name(problem_name: str) -> TechnicalProblemSchema:
    with session.begin() as s:
        return TechnicalProblemSchema.model_validate(
            s.query(TechnicalProblem)
            .filter(TechnicalProblem.problem_name == problem_name)
            .first()
        )


def get_last_technical_request_id() -> int:
    """
    Returns last technical request id in database.
    """
    with session.begin() as s:
        return s.query(func.max(TechnicalRequest.id)).first()[0]


def get_technical_problem_by_problem_name(problem_name: str) -> TechnicalProblemSchema:
    with session.begin() as s:
        return TechnicalProblemSchema.model_validate(
            s.query(TechnicalProblem)
            .filter(TechnicalProblem.problem_name == problem_name)
            .first()
        )


def create_technical_request(record: TechnicalRequestSchema) -> bool:
    """Creates technical problem
    Returns: `True` if technical problem request record created, `False` otherwise.
    """
    with session.begin() as s:
        technical_request = TechnicalRequest(
            problem_id=record.problem.id,
            description=record.description,
            state=record.state,
            score=None,
            open_date=record.open_date,
            deadline_date=record.deadline_date,
            repair_date=None,
            confirmation_date=None,
            reopen_date=None,
            close_date=None,
            worker_id=record.worker.id,
            territorial_manager_id=record.territorial_manager.id,
            repairman_id=record.repairman.id,
            department_id=record.department.id,
        )
        s.add(technical_request)

        for doc in record.problem_photos:
            file = TechnicalRequestProblemPhoto(
                technical_request=technical_request, document=doc.document
            )
            s.add(file)

    return True


def update_technical_request_from_repairman(record: TechnicalRequestSchema):
    with session.begin() as s:
        cur_request = (
            s.query(TechnicalRequest).filter(TechnicalRequest.id == record.id).first()
        )

        cur_request.state = record.state
        cur_request.repair_date = record.repair_date
        cur_request.reopen_repair_date = record.reopen_repair_date

        for doc in record.repair_photos:
            file = TechnicalRequestRepairPhoto(
                technical_request=cur_request, document=doc.document
            )
            s.add(file)
    return True


def update_technical_request_from_territorial_manager(record: TechnicalRequestSchema):
    with session.begin() as s:
        cur_request = (
            s.query(TechnicalRequest).filter(TechnicalRequest.id == record.id).first()
        )

        cur_request.state = record.state
        cur_request.close_date = record.close_date
        cur_request.reopen_date = record.reopen_date
        cur_request.reopen_deadline_date = record.reopen_deadline_date
        cur_request.confirmation_date = record.confirmation_date
        cur_request.reopen_confirmation_date = record.reopen_confirmation_date
        cur_request.score = record.score
        cur_request.confirmation_description = record.confirmation_description
        cur_request.close_description = record.close_description
        if record.acceptor_post:
            cur_request.acceptor_post = (
                s.query(Post).filter(Post.id == record.acceptor_post.id).first()
            )
    return True


def update_tech_request_executor(request_id: int, repairman_id: int):
    with session.begin() as s:
        cur_request = (
            s.query(TechnicalRequest).filter(TechnicalRequest.id == request_id).first()
        )
        repairman = s.query(Worker).filter(Worker.id == repairman_id)
        cur_request.executor = repairman
        cur_request.repairman_id = repairman_id
    return True


def update_technical_request_problem(request_id: int, problem_id: int):
    with session.begin() as s:
        cur_request = (
            s.query(TechnicalRequest).filter(TechnicalRequest.id == request_id).first()
        )
        cur_request.problem_id = problem_id
        problem = (
            s.query(TechnicalProblem).filter(TechnicalProblem.id == problem_id).first()
        )
        cur_request.problem = problem
    return True


def get_technical_requests_by_column(
    column: Any, value: Any
) -> list[TechnicalRequestSchema]:
    """
    Returns all `TechnicalRequest` as `TechnicalRequestSchema` in database
    by `column` with `value`.
    """
    return get_technical_requests_by_columns([column], [value])


def get_repairman_by_department_id_and_executor_type(
    department_id: int, executor_type: str
) -> Optional[WorkerSchema]:
    """
    Return WorkerSchema for territorial manager by department id
    """
    with session.begin() as s:
        repairman_id = None
        q = s.query(Department)
        match executor_type:
            case Executor.chief_technician.name:
                repairman_id: int = (
                    q.filter(Department.id == department_id).first().chief_technician_id
                )
            case Executor.technician.name:
                repairman_id: int = (
                    q.filter(Department.id == department_id).first().technician_id
                )
            case Executor.electrician.name:
                repairman_id: int = (
                    q.filter(Department.id == department_id).first().electrician_id
                )

        if repairman_id:
            return WorkerSchema.model_validate(
                s.query(Worker).filter(Worker.id == repairman_id).first()
            )
        else:
            return None


def get_territorial_manager_by_department_id(department_id: int) -> WorkerSchema:
    """
    Return WorkerSchema for territorial manager by department id
    """
    with session.begin() as s:
        territorial_manager: Worker = (
            s.query(Department).filter(Department.id == department_id).first()
        ).territorial_manager
        return WorkerSchema.model_validate(territorial_manager)


def get_technical_requests_by_columns(
    columns: list[Any], values: list[Any], history: bool = False
) -> list[TechnicalRequestSchema]:
    """
    Returns all TechnicalRequest as TechnicalRequestSchema by columns with values.
    """
    with session.begin() as s:
        query = s.query(TechnicalRequest)
        for column, value in zip(columns, values):
            query = query.filter(column == value)
        if history:
            query = query.filter(
                or_(
                    TechnicalRequest.state == ApprovalStatus.approved,
                    TechnicalRequest.state == ApprovalStatus.skipped,
                    TechnicalRequest.state == ApprovalStatus.not_relevant,
                )
            )
        raw_models = query.order_by(TechnicalRequest.id).all()
        return [
            TechnicalRequestSchema.model_validate(raw_model) for raw_model in raw_models
        ]


def get_all_technical_requests_in_department(
    department_id: int, history_flag: bool = False
) -> list[TechnicalRequestSchema]:
    """
    Returns all TechnicalRequest as TechnicalRequestSchema for department director.
    """
    with session.begin() as s:
        query = s.query(TechnicalRequest).filter(
            TechnicalRequest.department_id == department_id,
        )

        if history_flag:
            query = query.filter(
                or_(
                    TechnicalRequest.state == ApprovalStatus.approved,
                    TechnicalRequest.state == ApprovalStatus.skipped,
                    TechnicalRequest.state == ApprovalStatus.not_relevant,
                )
            )
        else:
            query = query.filter(
                and_(
                    TechnicalRequest.state != ApprovalStatus.approved,
                    TechnicalRequest.state != ApprovalStatus.skipped,
                    TechnicalRequest.state != ApprovalStatus.not_relevant,
                )
            )

        raw_models = query.order_by(TechnicalRequest.id).all()
        return [
            TechnicalRequestSchema.model_validate(raw_model) for raw_model in raw_models
        ]


def get_rework_tech_request(
    department_id: int, repairman_id: int
) -> list[TechnicalRequestSchema]:
    """
    Returns all TechnicalRequest as TechnicalRequestSchema by columns with values.
    """
    with session.begin() as s:
        raw_models = (
            s.query(TechnicalRequest)
            .filter(
                TechnicalRequest.department_id == department_id,
                TechnicalRequest.repairman_id == repairman_id,
                TechnicalRequest.reopen_repair_date == null(),
                TechnicalRequest.confirmation_date != null(),
                TechnicalRequest.state != ApprovalStatus.approved,
                TechnicalRequest.state != ApprovalStatus.skipped,
                TechnicalRequest.state != ApprovalStatus.not_relevant,
            )
            .order_by(TechnicalRequest.id)
            .all()
        )

        return [
            TechnicalRequestSchema.model_validate(raw_model) for raw_model in raw_models
        ]


def get_technical_requests_for_repairman_history(
    repairman_id: int, department_id: int
) -> list[TechnicalRequestSchema]:
    with session.begin() as s:
        raw_models = (
            s.query(TechnicalRequest)
            .filter(
                and_(
                    TechnicalRequest.repairman_id == repairman_id,
                    or_(
                        TechnicalRequest.state == ApprovalStatus.pending_approval,
                        TechnicalRequest.state == ApprovalStatus.approved,
                        TechnicalRequest.state == ApprovalStatus.skipped,
                        TechnicalRequest.state == ApprovalStatus.not_relevant,
                    ),
                    TechnicalRequest.department_id == department_id,
                )
            )
            .order_by(TechnicalRequest.id)
            .all()
        )
        return [
            TechnicalRequestSchema.model_validate(raw_model) for raw_model in raw_models
        ]


def get_departments_by_worker_id_and_worker_column(
    worker_column: Any,
    worker_id: int,
) -> list[DepartmentSchema]:
    with session.begin() as s:
        raw_models = s.query(Department).filter(worker_column == worker_id).all()
        return [DepartmentSchema.model_validate(raw_model) for raw_model in raw_models]


def get_departments_names_by_worker_id_and_worker_column(
    worker_column: Any,
    worker_id: int,
) -> list[DepartmentSchema]:
    with session.begin() as s:
        raw_models = s.query(Department).filter(worker_column == worker_id).all()
        return [
            (DepartmentSchema.model_validate(raw_model)).name
            for raw_model in raw_models
        ]


def get_departments_names_for_repairman(
    worker_id: int,
) -> list[DepartmentSchema]:
    with session.begin() as s:
        raw_models = s.query(Department).filter(
            or_(
                Department.technician_id == worker_id,
                Department.electrician_id == worker_id,
            )
        )
        return [
            (DepartmentSchema.model_validate(raw_model)).name
            for raw_model in raw_models
        ]


def get_all_active_requests_in_department(
    department_id: int,
) -> list[TechnicalRequestSchema]:
    with session.begin() as s:
        raw_models = (
            s.query(TechnicalRequest)
            .filter(
                TechnicalRequest.department_id == department_id,
                TechnicalRequest.close_date == null(),
            )
            .order_by()
            .all()
        )
        return [
            TechnicalRequestSchema.model_validate(raw_model) for raw_model in raw_models
        ]


def get_departments() -> list[DepartmentSchema]:
    with session.begin() as s:
        raw_models = s.query(Department).all()
        return [DepartmentSchema.model_validate(raw_model) for raw_model in raw_models]


def close_request(
    request_id: int,
    description: str,
    close_date: datetime,
    acceptor_post_id: int,
) -> int:
    """
    Close request by Chief Technician or Department Director
    Return creator TG id
    """
    with session.begin() as s:
        cur_request = (
            s.query(TechnicalRequest).filter(TechnicalRequest.id == request_id).first()
        )
        cur_request.state = ApprovalStatus.not_relevant
        cur_request.close_description = description
        cur_request.close_date = close_date
        cur_request.acceptor_post = (
            s.query(Post).filter(Post.id == acceptor_post_id).first()
        )
        return (WorkerSchema.model_validate(cur_request.worker)).telegram_id


# endregion


# region Model general
def get_model_count(
    model_type: Type[Base],
    query_schema: QuerySchema,
) -> int:
    """Return count of `model` in bd."""
    with session.begin() as s:
        query_builder = QueryBuilder(s.query(model_type))
        query_builder.apply(query_schema)

        return query_builder.query.count()


def get_models(
    model_type: Type[Base],
    schema_type: Type[BaseModel],
    page: int,
    records_per_page: int,
    query_schema: QuerySchema,
) -> list[BaseSchema]:
    """Returns `model_type` schemas with applied instructions.

    See `QueryBuilder.apply` for more info applied instructions.
    """
    with session.begin() as s:
        query_builder = QueryBuilder(s.query(model_type))
        query_builder.apply(query_schema)

        raw_models = query_builder.query.offset((page - 1) * records_per_page).limit(
            records_per_page
        )

        return [schema_type.model_validate(raw_model) for raw_model in raw_models]


def export_models(
    model_type: Type[Base],
    query_schema: QuerySchema,
    formatters: dict[str, Callable[[any], str]] = {},
    exclude_columns: list[str] = [],
    aliases: dict[str, str] = {},
) -> BytesIO:
    """Returns xlsx file with `model_type` records filtered by `query_schema`."""
    with session.begin() as s:
        query_builder = QueryBuilder(s.query(model_type))
        query_builder.apply(query_schema)
        exporter = XLSXExporter(
            query_builder.query, formatters, exclude_columns, aliases
        )

        return exporter.export()


# endregion


# region IT problem
def get_problems_it_columns() -> list[ProblemITSchema]:
    """
    Returns all existed IT problems in database.
    """
    with session.begin() as s:
        raw_models = s.query(ProblemIT).all()
        return [ProblemITSchema.model_validate(raw_model) for raw_model in raw_models]


def get_last_bid_it_id() -> int:
    """
    Returns last bid IT id in database.
    """
    with session.begin() as s:
        return s.query(func.max(BidIT.id)).first()[0]


def find_problem_it_by_id(column: any, value: any) -> ProblemITSchema:
    """
    Returns problem IT in database by `column` with `value`.
    If problem IT not exist return `None`.
    """
    with session.begin() as s:
        raw_worker = s.query(ProblemIT).filter(column == value).first()
        if not raw_worker:
            return None
        return ProblemITSchema.model_validate(raw_worker)


def get_bids_it_by_worker(worker: WorkerSchema) -> list[BidITSchema]:
    """
    Returns all bids IT in database by worker.
    """
    with session.begin() as s:
        raw_bids = s.query(BidIT).filter(BidIT.worker_id == worker.id).all()
        return [BidITSchema.model_validate(raw_bid) for raw_bid in raw_bids]


def get_history_bids_it_for_worker(worker: WorkerSchema) -> list[BidITSchema]:
    """
    Returns history bids IT in database by worker.
    """
    with session.begin() as s:
        raw_bids = (
            s.query(BidIT)
            .filter(
                and_(
                    BidIT.worker_id == worker.id,
                    or_(
                        BidIT.status == ApprovalStatus.approved,
                        BidIT.status == ApprovalStatus.skipped,
                    ),
                )
            )
            .all()
        )
        return [BidITSchema.model_validate(raw_bid) for raw_bid in raw_bids]


def find_bid_it_by_column(column: any, value: any) -> BidITSchema:
    """
    Returns bid IT in database by `column` with `value`.
    If bid not exist return `None`.
    """
    with session.begin() as s:
        raw_bid = s.query(BidIT).filter(column == value).first()
        if not raw_bid:
            return None
        return BidITSchema.model_validate(raw_bid)


def add_bid_it(bid_it: BidITSchema):
    """
    Adds `bid IT` to database.
    """
    with session.begin() as s:
        worker = s.query(Worker).filter(Worker.id == bid_it.worker.id).first()
        department = (
            s.query(Department).filter(Department.id == bid_it.department.id).first()
        )
        problem = s.query(ProblemIT).filter(ProblemIT.id == bid_it.problem.id).first()

        bid_model = BidIT(
            problem_comment=bid_it.problem_comment,
            problem_photos=[],
            problem=problem,
            department=department,
            worker=worker,
            status=bid_it.status,
            opening_date=bid_it.opening_date,
            repairman=problem.repairman,
            territorial_manager=department.territorial_manager,
        )

        s.add(bid_model)

        for document in bid_it.problem_photos:
            s.add(BidITWorkerDocument(bid_it=bid_model, document=document.document))


def get_pending_bids_it_by_worker(worker: WorkerSchema) -> list[BidITSchema]:
    """
    Returns all bids IT in database by worker.
    """
    with session.begin() as s:
        raw_bids = (
            s.query(BidIT)
            .filter(
                and_(
                    BidIT.worker_id == worker.id,
                    or_(
                        BidIT.status == ApprovalStatus.pending_approval,
                        BidIT.status == ApprovalStatus.pending,
                        BidIT.status == ApprovalStatus.denied,
                    ),
                )
            )
            .all()
        )
        return [BidITSchema.model_validate(raw_bid) for raw_bid in raw_bids]


def find_departments_by_column(column: any, value: any) -> list[DepartmentSchema]:
    """
    Returns departments in database by `column` with `value`.
    If department not exist return `[]`.
    """
    with session.begin() as s:
        raw_deparments = s.query(Department).filter(column == value).all()
        if not raw_deparments:
            return []
        return [
            DepartmentSchema.model_validate(raw_deparment)
            for raw_deparment in raw_deparments
        ]


def update_bid_it_rm(bid: BidITSchema):
    """Updates bid IT by repairman."""
    with session.begin() as s:
        cur_bid = s.query(BidIT).filter(BidIT.id == bid.id).first()
        if not cur_bid:
            return None

        cur_bid.status = bid.status
        cur_bid.done_date = bid.done_date
        cur_bid.reopen_done_date = bid.reopen_done_date

        for document in bid.work_photos:
            s.add(BidITRepairmanDocument(bid_it=cur_bid, document=document.document))


def get_bid_it_by_id(id: int) -> BidITSchema:
    """Gets bid IT by its id."""
    with session.begin() as s:
        raw_bid = s.query(BidIT).filter(BidIT.id == id).first()
        if not raw_bid:
            return None
        return BidITSchema.model_validate(raw_bid)


def update_bid_it_tm(bid: BidITSchema):
    """Updates bid IT by repairman."""
    with session.begin() as s:
        cur_bid = s.query(BidIT).filter(BidIT.id == bid.id).first()
        if not cur_bid:
            return None

        cur_bid.status = bid.status
        cur_bid.mark = bid.mark
        cur_bid.reopening_date = bid.reopening_date
        cur_bid.approve_date = bid.approve_date
        cur_bid.close_date = bid.close_date
        cur_bid.work_comment = bid.work_comment
        cur_bid.reopen_approve_date = bid.reopen_approve_date
        cur_bid.reopen_done_date = bid.reopen_done_date
        cur_bid.reopen_work_comment = bid.reopen_work_comment


def get_bids_it_by_repairman_with_status(
    repairman: WorkerSchema, department: DepartmentSchema, status: ApprovalStatus
) -> list[BidITSchema]:
    """
    Returns bids IT in database by repairman and department with status.
    """
    with session.begin() as s:
        raw_bids = (
            s.query(BidIT)
            .filter(
                and_(
                    BidIT.repairman_id == repairman.id,
                    BidIT.department_id == department.id,
                    BidIT.status == status,
                )
            )
            .all()
        )

        return [BidITSchema.model_validate(raw_bid) for raw_bid in raw_bids]


def get_history_bids_it_for_repairman(
    repairman: WorkerSchema, department: DepartmentSchema
) -> list[BidITSchema]:
    with session.begin() as s:
        raw_bids = (
            s.query(BidIT)
            .filter(
                and_(
                    BidIT.repairman_id == repairman.id,
                    BidIT.department_id == department.id,
                    or_(
                        BidIT.status == ApprovalStatus.approved,
                        BidIT.status == ApprovalStatus.skipped,
                    ),
                )
            )
            .all()
        )

        return [BidITSchema.model_validate(raw_bid) for raw_bid in raw_bids]


def get_pending_bids_it_for_territorial_manager(
    territorial_manager: WorkerSchema, department: DepartmentSchema
) -> list[BidITSchema]:
    with session.begin() as s:
        raw_bids = (
            s.query(BidIT)
            .filter(
                and_(
                    BidIT.territorial_manager_id == territorial_manager.id,
                    BidIT.department_id == department.id,
                    BidIT.status == ApprovalStatus.pending_approval,
                )
            )
            .all()
        )

        return [BidITSchema.model_validate(raw_bid) for raw_bid in raw_bids]


def get_history_bids_it_for_territorial_manager(
    territorial_manager: WorkerSchema, department: DepartmentSchema
) -> list[BidITSchema]:
    with session.begin() as s:
        raw_bids = (
            s.query(BidIT)
            .filter(
                and_(
                    BidIT.territorial_manager_id == territorial_manager.id,
                    BidIT.department_id == department.id,
                    or_(
                        BidIT.status == ApprovalStatus.approved,
                        BidIT.status == ApprovalStatus.skipped,
                    ),
                )
            )
            .all()
        )

        return [BidITSchema.model_validate(raw_bid) for raw_bid in raw_bids]


def find_repairman_it_by_department(department_name: str) -> WorkerSchema:
    with session.begin() as s:
        raw_department = (
            s.query(Department).filter(Department.name == department_name).first()
        )
        if not raw_department:
            return None
        return WorkerSchema.model_validate(raw_department.it_repairman)


# endregion


def get_logins(worker_id: int) -> Optional[AccountLoginsSchema]:
    with session.begin() as s:
        q = s.query(AccountLogins).filter(AccountLogins.worker_id == worker_id).first()
        if q is None:
            return None
        return AccountLoginsSchema.model_validate(q)


def get_subordination_chief(worker_id: int) -> Optional[WorkerSchema]:
    with session.begin() as s:
        subordination = (
            s.query(Subordination)
            .filter(Subordination.employee_id == worker_id)
            .first()
        )
        if subordination is None:
            return None
        try:
            raw_chief = get_workers_with_post_by_column(
                Worker.id, subordination.chief_id
            )[0]
        except IndexError:
            return None
        return WorkerSchema.model_validate(raw_chief)


def get_material_values(worker_id) -> list[MaterialValuesSchema]:
    with session.begin() as s:
        material_values = (
            s.query(MaterialValues).filter(MaterialValues.worker_id == worker_id).all()
        )
        return [
            MaterialValuesSchema.model_validate(material_value)
            for material_value in material_values
        ]


def get_material_value_by_inventory_number(
    inventory_number: int,
) -> MaterialValuesSchema:
    with session.begin() as s:
        material_value = (
            s.query(MaterialValues)
            .filter(MaterialValues.inventory_number == inventory_number)
            .first()
        )
        return MaterialValuesSchema.model_validate(material_value)
