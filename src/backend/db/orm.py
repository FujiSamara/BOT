from typing import Any
from db.database import Base, engine, session
from db.models import (
    Bid,
    BudgetRecord,
    Expenditure,
    Post,
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
)
from db.schemas import (
    BidSchema,
    BudgetRecordSchema,
    DepartmentSchema,
    ExpenditureSchema,
    WorkerBidSchema,
    WorkerSchema,
    WorkTimeSchema,
    PostSchema,
    ProblemITSchema,
    BidITSchema,
)
from sqlalchemy.sql.expression import func
from sqlalchemy import or_, and_, desc


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


def find_department_by_column(column: any, value: any) -> DepartmentSchema:
    """
    Returns department in database by `column` with `value`.
    If department not exist return `None`.
    """
    with session.begin() as s:
        raw_deparment = s.query(Department).filter(column == value).first()
        if not raw_deparment:
            return None
        return DepartmentSchema.model_validate(raw_deparment)


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


def add_bid(bid: BidSchema):
    """
    Adds `bid` to database.
    """
    with session.begin() as s:
        worker = s.query(Worker).filter(Worker.id == bid.worker.id).first()
        department = (
            s.query(Department).filter(Department.id == bid.department.id).first()
        )

        bid = Bid(
            amount=bid.amount,
            payment_type=bid.payment_type,
            purpose=bid.purpose,
            agreement=bid.agreement,
            urgently=bid.urgently,
            need_document=bid.need_document,
            comment=bid.comment,
            create_date=bid.create_date,
            department=department,
            worker=worker,
            document=bid.document,
            document1=bid.document1,
            document2=bid.document2,
            kru_state=bid.kru_state,
            owner_state=bid.owner_state,
            accountant_card_state=bid.accountant_card_state,
            accountant_cash_state=bid.accountant_cash_state,
            teller_card_state=bid.teller_card_state,
            teller_cash_state=bid.teller_cash_state,
        )

        s.add(bid)


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
                        Bid.accountant_card_state == ApprovalStatus.pending_approval,
                        Bid.accountant_cash_state == ApprovalStatus.pending_approval,
                        Bid.teller_card_state == ApprovalStatus.pending_approval,
                        Bid.teller_cash_state == ApprovalStatus.pending_approval,
                        Bid.kru_state == ApprovalStatus.pending_approval,
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

        cur_bid.amount = bid.amount
        cur_bid.payment_type = bid.payment_type
        cur_bid.purpose = bid.purpose
        cur_bid.agreement = bid.agreement
        cur_bid.urgently = bid.urgently
        cur_bid.need_document = bid.need_document
        cur_bid.comment = bid.comment
        cur_bid.denying_reason = bid.denying_reason
        cur_bid.create_date = bid.create_date
        cur_bid.close_date = bid.close_date
        cur_bid.department = new_department
        cur_bid.worker = new_worker
        # TODO: Update documents
        # cur_bid.document = bid.document
        # cur_bid.document1 = bid.document1
        # cur_bid.document2 = bid.document2
        cur_bid.kru_state = bid.kru_state
        cur_bid.owner_state = bid.owner_state
        cur_bid.accountant_card_state = bid.accountant_card_state
        cur_bid.accountant_cash_state = bid.accountant_cash_state
        cur_bid.teller_card_state = bid.teller_card_state
        cur_bid.teller_cash_state = bid.teller_cash_state


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
        return [WorkerSchema.model_validate(raw_wodel) for raw_wodel in raw_models]


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
        return [WorkTimeSchema.model_validate(raw_wodel) for raw_wodel in raw_models]


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
        return [PostSchema.model_validate(raw_wodel) for raw_wodel in raw_models]


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
        cc_supervisor = (
            s.query(Worker).filter(Worker.id == expenditure.cc_supervisor.id).first()
        )
        creator = s.query(Worker).filter(Worker.id == expenditure.creator.id).first()

        if not cc or not fac or not cc_supervisor or not creator:
            return False

        expenditure_model = Expenditure(
            name=expenditure.name,
            chapter=expenditure.chapter,
            create_date=expenditure.create_date,
            fac=fac,
            cc=cc,
            cc_supervisor=cc_supervisor,
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
        cc_supervisor = (
            s.query(Worker).filter(Worker.id == expenditure.cc_supervisor.id).first()
        )

        if not old or not cc or not fac or not cc_supervisor:
            return False

        old.name = expenditure.name
        old.chapter = expenditure.chapter
        old.create_date = expenditure.create_date
        old.fac = fac
        old.cc = cc
        old.cc_supervisor = cc_supervisor

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

        bid = BidIT(
            problem_comment=bid_it.problem_comment,
            problem_photo=bid_it.problem_photo,
            problem=problem,
            department=department,
            worker=worker,
            status=bid_it.status,
            opening_date=bid_it.opening_date,
            done_date=None,
            reopening_date=None,
            approve_date=None,
            close_date=None,
            mark=None,
            repairman=None,
            work_photo=None,
            work_comment=None,
        )

        s.add(bid)
