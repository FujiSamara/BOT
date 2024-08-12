from typing import Any
from db.database import Base, engine, session
from db.models import (
    Bid,
    BidDocument,
    BudgetRecord,
    Executor,
    Expenditure,
    FujiScope,
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
)
from db.schemas import (
    BidSchema,
    BudgetRecordSchema,
    DepartmentSchema,
    ExpenditureSchema,
    ProblemSchema,
    TechnicalRequestSchema,
    WorkerBidSchema,
    WorkerSchema,
    WorkTimeSchema,
    PostSchema,
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
            kru_state=bid.kru_state,
            owner_state=bid.owner_state,
            accountant_card_state=bid.accountant_card_state,
            accountant_cash_state=bid.accountant_cash_state,
            teller_card_state=bid.teller_card_state,
            teller_cash_state=bid.teller_cash_state,
            fac_state=bid.fac_state,
            cc_state=bid.cc_state,
            cc_supervisor_state=bid.cc_supervisor_state,
            expenditure=expenditure,
        )
        s.add(bid_model)

        for document in bid.documents:
            s.add(BidDocument(bid=bid_model, document=document.document))


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
        cur_bid.kru_state = bid.kru_state
        cur_bid.owner_state = bid.owner_state
        cur_bid.accountant_card_state = bid.accountant_card_state
        cur_bid.accountant_cash_state = bid.accountant_cash_state
        cur_bid.teller_card_state = bid.teller_card_state
        cur_bid.teller_cash_state = bid.teller_cash_state
        cur_bid.fac_state = bid.fac_state
        cur_bid.cc_state = bid.cc_state
        cur_bid.cc_supervisor_state = bid.cc_supervisor_state


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


# region Technical problem


def get_technical_problems() -> list[ProblemSchema]:
    """Returns list of ProblemSchema"""
    with session.begin() as s:
        raw_models = s.query(TechnicalProblem).all()
        return [ProblemSchema.model_validate(raw_model) for raw_model in raw_models]


def get_last_technical_request_id() -> int:
    """
    Returns last technical request id in database.
    """
    with session.begin() as s:
        return s.query(func.max(TechnicalRequest.id)).first()[0]


def get_technical_problem_by_problem_name(problem_name: str) -> ProblemSchema:
    with session.begin() as s:
        return ProblemSchema.model_validate(
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

    return True


def get_technical_requests_by_column(
    column: Any, value: Any
) -> list[TechnicalRequestSchema]:
    """
    Returns all `TechnicalReques` as `TechnicalRequesSchema` in database
    by `column` with `value`.
    """
    return get_technical_requests_by_columns([column], [value])


def get_repairman_by_department_id_and_executor_type(
    department_id: int, executor_type: str
) -> WorkerSchema | None:
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
        territorial_manager_id: int = (
            s.query(Department)
            .with_entities(Department.territorial_manager_id)
            .filter(Department.id == department_id)
            .first()
        )
        return WorkerSchema.model_validate(
            s.query(Worker).filter(Worker.id == territorial_manager_id).first()
        )


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
                )
            )
        raw_models = query.order_by(TechnicalRequest.id.desc()).limit(15).all()
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
                TechnicalRequest.reopen_repair_date == None,
                TechnicalRequest.reopen_date != None,
            )
            .order_by(TechnicalRequest.id.desc())
            .limit(15)
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
                    ),
                    TechnicalRequest.department_id == department_id,
                )
            )
            .order_by(TechnicalRequest.id.desc())
            .limit(15)
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


def get_all_active_requests_in_department(
    department_id: int,
) -> list[TechnicalRequestSchema]:
    with session.begin() as s:
        raw_models = (
            s.query(TechnicalRequest)
            .filter(
                TechnicalRequest.department_id == department_id,
                TechnicalRequest.close_date == None,
            )
            .order_by(TechnicalRequest.id.desc())
            .limit(15)
            .all()
        )
        return [
            TechnicalRequestSchema.model_validate(raw_model) for raw_model in raw_models
        ]


def get_all_repairmans_in_department(
    department_name: str,
) -> list[WorkerSchema]:
    with session.begin() as s:
        raw_model = (
            s.query(Department).filter(Department.name == department_name).first()
        )

        return [
            WorkerSchema.model_validate(executor)
            for executor in [
                raw_model.chief_technician,
                raw_model.technician,
                raw_model.electrician,
            ]
        ]


def update_tech_request_executor(request_id: int, repairman_id: int):
    with session.begin() as s:
        cur_request = (
            s.query(TechnicalRequest).filter(TechnicalRequest.id == request_id).first()
        )
        repairman = s.query(Worker).filter(Worker.id == repairman_id)
        cur_request.executor = repairman
        cur_request.repairman_id = repairman_id
    return True


# endregion
