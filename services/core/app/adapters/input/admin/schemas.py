# sqladmin shemas
from fastapi import Request
from fastapi.responses import RedirectResponse
from sqladmin import ModelView, action
from sqlalchemy import Select, or_, select

from app.infra.database.models import (
    PostScope,
    TechnicalProblem,
    Worker,
    Company,
    Department,
    Post,
    WorkerBid,
    WorkerBidDocument,
    ApprovalStatus,
    TechnicalRequest,
    Group,
    WorkTime,
    AccountLogins,
    Subordination,
    MaterialValues,
    WorkerFingerprint,
    FingerprintAttempt,
    WorkerDocument,
    WorkerChildren,
)
from app.adapters.input.admin.converters import (
    TechnicalRequestConverter,
    PostScopeConverter,
    WorkerConverter,
)
from app.infra.database.converters import (
    approval_status_dict,
    approval_status_technical_request_dict,
    worker_status_dict,
    gender_decode_dict,
)
from app.adapters.bot.kb import payment_type_dict
from app.schemas import FileOutSchema
from app import services
from app.adapters.input.api.auth import encrypt_password


class PostScopeView(ModelView, model=PostScope):
    column_list = [PostScope.post, PostScope.scope]
    column_searchable_list = [PostScope.scope]
    form_columns = [PostScope.scope, PostScope.post]
    column_details_exclude_list = [PostScope.post_id, PostScope.id]
    can_export = False
    can_edit = False
    form_converter = PostScopeConverter
    name_plural = "Доступы"
    name = "Доступ"
    column_labels = {
        PostScope.post: "Должность",
        PostScope.scope: "Доступ",
    }


class PostView(ModelView, model=Post):
    column_list = [Post.id, Post.name, Post.level, Post.salary]
    column_searchable_list = [Post.name, Post.level]
    form_columns = [Post.name, Post.level, Post.salary]
    column_details_exclude_list = [Post.work_times, Post.workers_bids]
    can_export = False

    name_plural = "Должности"
    name = "Должность"
    column_labels = {
        Post.name: "Название",
        Post.level: "Уровень доступа",
        Post.workers: "Сотрудники",
        Post.salary: "Зарплата",
        Post.scopes: "Доступы",
    }


class CompanyView(ModelView, model=Company):
    column_list = [Company.id, Company.name]
    column_details_exclude_list = [
        Company.work_times,
    ]
    column_searchable_list = [Company.name]
    form_columns = [Company.name]
    can_export = False

    name_plural = "Компании"
    name = "Компания"
    column_labels = {
        Company.name: "Название",
        Company.departments: "Предприятия",
        Company.workers: "Сотрудники",
    }


class DepartmentView(ModelView, model=Department):
    column_list = [Department.id, Department.name]
    column_searchable_list = [Department.name]
    column_details_exclude_list = [
        Department.company_id,
        Department.work_times,
        Department.workers_bids,
        Department.bids,
        Department.delivery_manager_id,
        Department.territorial_manager_id,
        Department.restaurant_manager_id,
        Department.territorial_director_id,
        Department.territorial_brand_chef_id,
        Department.technical_requests,
        Department.budget_records,
        Department.technician_id,
        Department.electrician_id,
        Department.chief_technician_id,
        Department.bids_it,
        Department.it_repairman_id,
    ]
    form_excluded_columns = [
        Department.workers,
        Department.bids,
        Department.work_times,
        Department.workers_bids,
        Department.technical_requests,
        Department.budget_records,
    ]
    can_export = False

    name_plural = "Предприятия"
    name = "Предприятие"
    column_labels = {
        Department.name: "Название",
        Department.address: "Адрес",
        Department.workers: "Сотрудники",
        Department.bids: "Заявки",
        Department.company: "Компания",
        Department.type: "Формат",
        Department.city: "Город",
        Department.opening_date: "Дата открытия",
        Department.closing_date: "Дата закрытия",
        Department.area: "Общая площадь",
        Department.territorial_manager: "Территориальный управляющий",
        Department.restaurant_manager: "Управляющий рестораном",
        Department.territorial_brand_chef: "Территориальный брендшеф",
        Department.delivery_manager: "Менеджер доставки",
        Department.territorial_director: "Территориальный директор",
        Department.chief_technician: "Главный техник",
        Department.technician: "Техник",
        Department.electrician: "Электрик",
        Department.it_repairman: "IT ремотник",
        Department.fingerprint_device_hex: "Номер СКУД устройства",
    }

    form_ajax_refs = {
        "company": {
            "fields": ("name",),
            "order_by": "name",
        },
        "delivery_manager": {
            "fields": ("l_name", "f_name", "o_name"),
            "order_by": "l_name",
        },
        "territorial_manager": {
            "fields": ("l_name", "f_name", "o_name"),
            "order_by": "l_name",
        },
        "restaurant_manager": {
            "fields": ("l_name", "f_name", "o_name"),
            "order_by": "l_name",
        },
        "territorial_director": {
            "fields": ("l_name", "f_name", "o_name"),
            "order_by": "l_name",
        },
        "territorial_brand_chef": {
            "fields": ("l_name", "f_name", "o_name"),
            "order_by": "l_name",
        },
        "chief_technician": {
            "fields": ("l_name", "f_name", "o_name"),
            "order_by": "l_name",
        },
        "technician": {
            "fields": ("l_name", "f_name", "o_name"),
            "order_by": "l_name",
        },
        "electrician": {
            "fields": ("l_name", "f_name", "o_name"),
            "order_by": "l_name",
        },
    }


class GroupView(ModelView, model=Group):
    column_list = [
        Group.id,
        Group.name,
    ]
    column_searchable_list = [
        Group.name,
    ]
    form_columns = [
        Group.name,
    ]
    can_export = False

    name_plural = "Отделы"
    name = "Отдел"
    column_labels = {
        Group.name: "Название",
        Group.workers: "Сотрудники",
    }


class WorkerView(ModelView, model=Worker):
    details_template = "worker_details.html"
    column_searchable_list = [
        Worker.f_name,
        Worker.l_name,
        Worker.o_name,
        Worker.phone_number,
    ]
    column_sortable_list = [
        Worker.state,
        Worker.id,
        Worker.post,
        Worker.employment_date,
    ]
    column_list = [
        Worker.l_name,
        Worker.f_name,
        Worker.phone_number,
        Worker.state,
        Worker.post,
        Worker.employment_date,
    ]

    column_details_list = [
        Worker.l_name,
        Worker.f_name,
        Worker.o_name,
        Worker.post,
        Worker.state,
        Worker.subordination_chief,
        Worker.phone_number,
        Worker.department,
        Worker.company,
        Worker.group,
        Worker.b_date,
        Worker.telegram_id,
        Worker.gender,
        Worker.employment_date,
        Worker.official_employment_date,
        Worker.dismissal_date,
        Worker.official_dismissal_date,
        Worker.medical_records_availability,
        Worker.citizenship,
        Worker.can_use_crm,
        Worker.documents,
        Worker.snils,
        Worker.inn,
        Worker.registration,
        Worker.actual_residence,
        Worker.children,
        Worker.children_born_date,
        Worker.military_ticket,
        Worker.patent,
        Worker.official_work,
    ]
    can_export = False

    name_plural = "Сотрудники"
    name = "Сотрудник"
    column_labels = {
        Worker.f_name: "Имя",
        Worker.l_name: "Фамилия",
        Worker.o_name: "Отчество",
        Worker.state: "Статус",
        Worker.subordination_chief: "Руководитель",
        Worker.department: "Предприятие",
        Worker.group: "Отдел",
        Worker.post: "Должность",
        Worker.b_date: "Дата рождения",
        Worker.bids: "Заявки",
        Worker.phone_number: "Номер телефона",
        Worker.company: "Компания",
        Worker.telegram_id: "ID телеграмм",
        Worker.employment_date: "Дата приёма",
        Worker.official_employment_date: "Официальная дата приёма",
        Worker.dismissal_date: "Дата увольнения",
        Worker.official_dismissal_date: "Официальная дата увольнения",
        Worker.medical_records_availability: "Наличие медицинской книжки",
        Worker.gender: "Пол",
        Worker.citizenship: "Гражданство",
        Worker.can_use_crm: "Может использовать CRM",
        Worker.password: "Пароль",
        Worker.documents: "Документы",
        Worker.snils: "СНИЛС",
        Worker.inn: "ИНН",
        Worker.registration: "Регистрация",
        Worker.actual_residence: "Фактическое место жительства",
        Worker.children: "Дети",
        Worker.children_born_date: "Даты рождения детей",
        Worker.military_ticket: "Военный билет",
        Worker.patent: "Патент",
        Worker.official_work: "Официально трудоустроен",
    }

    form_columns = [
        Worker.f_name,
        Worker.l_name,
        Worker.o_name,
        Worker.state,
        Worker.phone_number,
        Worker.department,
        Worker.group,
        Worker.telegram_id,
        Worker.post,
        Worker.b_date,
        Worker.employment_date,
        Worker.official_employment_date,
        Worker.dismissal_date,
        Worker.official_dismissal_date,
        Worker.medical_records_availability,
        Worker.gender,
        Worker.citizenship,
        Worker.can_use_crm,
        Worker.password,
        Worker.documents,
        Worker.snils,
        Worker.inn,
        Worker.registration,
        Worker.actual_residence,
        Worker.children,
        Worker.children_born_date,
        Worker.military_ticket,
        Worker.patent,
        Worker.official_work,
    ]

    form_ajax_refs = {
        "department": {
            "fields": ("name",),
            "order_by": "name",
        },
        "post": {
            "fields": ("name",),
            "order_by": "name",
        },
        "group": {
            "fields": ("name",),
            "order_by": "name",
        },
    }

    @staticmethod
    def gender_format(inst, column):
        value = getattr(inst, column)
        return gender_decode_dict.get(value)

    @staticmethod
    def worker_status_format(inst, column):
        value = getattr(inst, column)
        return worker_status_dict.get(value)

    @staticmethod
    def files_format(inst, column):
        documents: list[WorkerDocument] = getattr(inst, column)
        urls: list[FileOutSchema] = []
        for doc in documents:
            url = services.get_file_data(doc.document)
            if url:
                urls.append(url)

        return urls

    @staticmethod
    def search_query(stmt: Select, term: str):
        or_stmt = or_(
            Worker.f_name.ilike(f"%{term}%"),
            Worker.l_name.ilike(f"%{term}%"),
            Worker.o_name.ilike(f"%{term}%"),
        )

        for state, text in worker_status_dict.items():
            if text.lower() == term.lower():
                or_stmt = Worker.state == state
                break

        workers = select(Worker).filter(or_stmt)
        return workers

    async def on_model_change(self, data: dict, model: Worker, is_created, request):
        if "password" in data and data["password"] != model.password:
            data["password"] = encrypt_password(data["password"])

    def sort_query(self, stmt, request: Request):
        from sqlalchemy import asc, desc

        sort_by = request.query_params.get("sortBy", None)
        sort = request.query_params.get("sort", "asc")

        if sort_by:
            sort_fields = [(sort_by, sort == "desc")]
        else:
            sort_fields = self._get_default_sort()

        for sort_field, is_desc in sort_fields:
            model = self.model

            if sort_field == "post":
                sort_field = sort_field + "_id"

            if is_desc:
                stmt = stmt.order_by(desc(getattr(model, sort_field)))
            else:
                stmt = stmt.order_by(asc(getattr(model, sort_field)))

        return stmt

    column_formatters = {
        Worker.gender: gender_format,
        Worker.state: worker_status_format,
        Worker.documents: files_format,
    }
    column_formatters_detail = column_formatters

    form_converter = WorkerConverter


class WorkerDocumentView(ModelView, model=WorkerDocument):
    name = "Документ сотрудника"
    name_plural = "Документы сотрудников"

    can_create = True
    can_edit = True
    can_export = False

    column_list = [
        WorkerDocument.id,
        WorkerDocument.worker,
        WorkerDocument.document,
    ]

    column_sortable_list = [
        WorkerDocument.id,
    ]

    column_labels = {
        WorkerDocument.worker: "Сотрудник",
        WorkerDocument.document: "Документ",
    }

    form_ajax_refs = {
        "worker": {
            "fields": ("l_name", "f_name", "o_name"),
            "order_by": "l_name",
        },
    }

    @staticmethod
    def search_query(stmt: Select, term):
        workers_id = select(Worker.id).filter(
            or_(
                Worker.f_name.ilike(f"%{term}%"),
                Worker.l_name.ilike(f"%{term}%"),
                Worker.o_name.ilike(f"%{term}%"),
            )
        )

        return select(WorkerDocument).filter(
            WorkerDocument.worker_id.in_(workers_id),
        )

    async def on_model_change(
        self, data: dict, model: WorkerDocument, is_created, request
    ):
        from pathlib import Path

        if "document" in data and "worker" in data:
            worker_id = int(data["worker"])
            document = data["document"]
            filename = f"photo_worker_document_{worker_id}"
            filename += (
                f"_{services.get_last_worker_passport_id(worker_id=worker_id) + 1}"
            )
            filename += f"{Path(document.filename).suffix}"
            data["document"].filename = filename

    column_searchable_list = [
        "Фамилия",
        "Имя",
        "Отчество",
    ]


class WorkerChildrenView(ModelView, model=WorkerChildren):
    name = "Дети сотрудника"
    name_plural = "Дети сотрудников"

    can_create = True
    can_edit = True
    can_export = False

    column_list = [
        WorkerChildren.id,
        WorkerChildren.worker,
        WorkerChildren.born_date,
    ]

    column_sortable_list = [
        WorkerChildren.id,
    ]

    column_labels = {
        WorkerChildren.worker: "Сотрудник",
        WorkerChildren.born_date: "Дата рождения",
    }

    form_ajax_refs = {
        "worker": {
            "fields": ("l_name", "f_name", "o_name"),
            "order_by": "l_name",
        },
    }

    @staticmethod
    def search_query(stmt: Select, term):
        workers_id = select(Worker.id).filter(
            or_(
                Worker.f_name.ilike(f"%{term}%"),
                Worker.l_name.ilike(f"%{term}%"),
                Worker.o_name.ilike(f"%{term}%"),
            )
        )

        return select(WorkerChildren).filter(
            WorkerChildren.worker_id.in_(workers_id),
        )

    column_searchable_list = [
        "Фамилия",
        "Имя",
        "Отчество",
    ]


class WorkerBidView(ModelView, model=WorkerBid):
    details_template = "worker_bid_details.html"

    column_labels = {
        WorkerBid.f_name: "Имя",
        WorkerBid.l_name: "Фамилия",
        WorkerBid.o_name: "Отчество",
        WorkerBid.post: "Должность",
        WorkerBid.department: "Предприятия",
        WorkerBid.work_permission: "Разрешение на работу",
        WorkerBid.worksheet: "Анкета",
        WorkerBid.passport: "Документы",
        WorkerBid.state: "Статус",
        WorkerBid.create_date: "Дата создания",
        WorkerBid.comment: "Комментарий",
        WorkerBid.official_work: "Официальное трудоустройство",
        WorkerBid.close_date: "Дата закрытия заявки",
    }

    column_list = [
        WorkerBid.id,
        WorkerBid.l_name,
        WorkerBid.f_name,
        WorkerBid.o_name,
        WorkerBid.post,
        WorkerBid.department,
        WorkerBid.state,
        WorkerBid.close_date,
    ]

    column_details_list = [
        WorkerBid.create_date,
        WorkerBid.l_name,
        WorkerBid.f_name,
        WorkerBid.o_name,
        WorkerBid.worksheet,
        WorkerBid.passport,
        WorkerBid.work_permission,
        WorkerBid.post,
        WorkerBid.department,
        WorkerBid.state,
        WorkerBid.comment,
        WorkerBid.official_work,
        WorkerBid.close_date,
    ]

    column_searchable_list = [WorkerBid.f_name, WorkerBid.l_name, WorkerBid.o_name]

    column_sortable_list = [
        WorkerBid.create_date,
        WorkerBid.l_name,
        WorkerBid.id,
        WorkerBid.o_name,
        WorkerBid.f_name,
        WorkerBid.state,
        WorkerBid.post,
        WorkerBid.close_date,
    ]

    form_columns = [WorkerBid.comment]

    @staticmethod
    def datetime_format(inst, column):
        format = "%H:%M %d.%m.%y"
        value = getattr(inst, column)
        if value:
            return value.strftime(format)
        else:
            return "Заявка не закрыта"

    @staticmethod
    def payment_type_format(inst, column):
        value = getattr(inst, column)
        return payment_type_dict.get(value)

    @staticmethod
    def approval_status_format(inst, column):
        value = getattr(inst, column)
        return approval_status_dict.get(value)

    @action(
        name="approve_worker_bid",
        label="Согласовать",
        add_in_detail=True,
    )
    async def approve_worker_bid(self, request: Request):
        pk = int(request.query_params.get("pks", "").split(",")[0])
        await services.update_worker_bid_state(ApprovalStatus.approved, pk)

        return RedirectResponse(request.url_for("admin:list", identity=self.identity))

    @action(
        name="decline_worker_bid",
        label="Отказать",
        add_in_detail=True,
    )
    async def decline_worker_bid(self, request: Request):
        pk = int(request.query_params.get("pks", "").split(",")[0])
        await services.update_worker_bid_state(ApprovalStatus.denied, pk)

        return RedirectResponse(request.url_for("admin:list", identity=self.identity))

    @staticmethod
    def files_format(inst, column):
        documents: list[WorkerBidDocument] = getattr(inst, column)
        urls: list[FileOutSchema] = []
        for doc in documents:
            url = services.get_file_data(doc.document)
            if url:
                urls.append(url)

        return urls

    @staticmethod
    def search_query(stmt: Select, term: str):
        or_stmt = or_(
            WorkerBid.f_name.ilike(f"%{term}%"),
            WorkerBid.l_name.ilike(f"%{term}%"),
            WorkerBid.o_name.ilike(f"%{term}%"),
        )

        for state, text in approval_status_dict.items():
            if text.lower() == term.lower():
                or_stmt = WorkerBid.state == state
                break

        workers = select(WorkerBid).filter(or_stmt)
        return workers

    can_create = False
    can_export = False
    name_plural = "Заявки на работу"
    name = "Заявка на работу"

    column_formatters = {
        WorkerBid.state: approval_status_format,
        WorkerBid.passport: files_format,
        WorkerBid.work_permission: files_format,
        WorkerBid.worksheet: files_format,
        WorkerBid.create_date: datetime_format,
    }

    column_formatters_detail = column_formatters

    def sort_query(self, stmt, request: Request):
        from sqlalchemy import asc, desc

        sort_by = request.query_params.get("sortBy", None)
        sort = request.query_params.get("sort", "asc")

        if sort_by:
            sort_fields = [(sort_by, sort == "desc")]
        else:
            sort_fields = self._get_default_sort()

        for sort_field, is_desc in sort_fields:
            model = self.model

            if sort_field == "post":
                sort_field = sort_field + "_id"

            if is_desc:
                stmt = stmt.order_by(desc(getattr(model, sort_field)))
            else:
                stmt = stmt.order_by(asc(getattr(model, sort_field)))

        return stmt


class TechnicalRequestView(ModelView, model=TechnicalRequest):
    details_template = "tech_req_details.html"

    column_labels = {
        TechnicalRequest.description: "описание проблемы",
        TechnicalRequest.state: "Статус выполнения",
        TechnicalRequest.score: "Оценка ТУ",
        TechnicalRequest.open_date: "Дата открытия заявки",
        TechnicalRequest.deadline_date: "Крайний срок ремонта",
        TechnicalRequest.repair_date: "Дата ремонта",
        TechnicalRequest.confirmation_date: "Дата утверждения ремонта",
        TechnicalRequest.confirmation_description: "Описания доработки",
        TechnicalRequest.reopen_date: "Дата пере открытия",
        TechnicalRequest.reopen_deadline_date: "Крайний срок ремонта при пере открытие",
        TechnicalRequest.reopen_repair_date: "Дата повторного ремонта",
        TechnicalRequest.reopen_confirmation_date: "Дата повторного утверждения",
        TechnicalRequest.close_date: "Дата закрытия заявки",
        TechnicalRequest.close_description: "Комментарий ТУ при закрытие заявки",
        TechnicalRequest.repair_photos: "Фотографии ремонта",
        TechnicalRequest.problem_photos: "Фотографии проблемы",
        TechnicalRequest.repairman: "Исполнитель",
        TechnicalRequest.department: "Предприятие",
        TechnicalRequest.problem: "Проблема",
        TechnicalRequest.appraiser: "Территориальный менеджер/управляющий",
        TechnicalRequest.worker: "Создатель",
        TechnicalRequest.acceptor_post: "Должность закрывшего",
        TechnicalRequest.repairman_worktime: "Заявка в исполнение",
    }

    column_list = [
        TechnicalRequest.id,
        TechnicalRequest.department,
        TechnicalRequest.problem,
        TechnicalRequest.repairman,
        TechnicalRequest.state,
        TechnicalRequest.description,
    ]

    column_details_exclude_list = [
        TechnicalRequest.department_id,
        TechnicalRequest.worker_id,
        TechnicalRequest.problem_id,
        TechnicalRequest.repairman_id,
        TechnicalRequest.department_id,
        TechnicalRequest.appraiser_id,
        TechnicalRequest.acceptor_post_id,
    ]
    form_excluded_columns = [
        TechnicalRequest.problem_photos,
        TechnicalRequest.repair_photos,
        TechnicalRequest.repairman_worktime,
    ]

    column_sortable_list = [
        TechnicalRequest.id,
        TechnicalRequest.state,
        TechnicalRequest.department,
        TechnicalRequest.repairman,
    ]

    @staticmethod
    def search_query(stmt: Select, term):
        # Searches corresponding depatrmtens and problems
        deps = select(Department.id).filter(Department.name.ilike(f"%{term}%"))
        probs = select(TechnicalProblem.id).filter(
            TechnicalProblem.problem_name.ilike(f"%{term}%")
        )

        # Chooses requests with found deps or probs.
        return select(TechnicalRequest).filter(
            or_(
                TechnicalRequest.department_id.in_(deps),
                TechnicalRequest.problem_id.in_(probs),
            )
        )

    column_searchable_list = [TechnicalRequest.department, TechnicalRequest.problem]

    can_create = False
    can_edit = True
    can_export = False
    name_plural = "Технические заявки"
    name = "Техническая заявка"

    @staticmethod
    def files_format(inst, column):
        return WorkerBidView.files_format(inst, column)

    @staticmethod
    def approval_status_format(inst, column):
        value = getattr(inst, column)
        return approval_status_technical_request_dict.get(value)

    column_formatters = {
        TechnicalRequest.state: approval_status_format,
        TechnicalRequest.repair_photos: files_format,
        TechnicalRequest.problem_photos: files_format,
        TechnicalRequest.open_date: WorkerBidView.datetime_format,
        TechnicalRequest.close_date: WorkerBidView.datetime_format,
        TechnicalRequest.reopen_date: WorkerBidView.datetime_format,
        TechnicalRequest.repair_date: WorkerBidView.datetime_format,
        TechnicalRequest.deadline_date: WorkerBidView.datetime_format,
        TechnicalRequest.confirmation_date: WorkerBidView.datetime_format,
        TechnicalRequest.reopen_repair_date: WorkerBidView.datetime_format,
        TechnicalRequest.reopen_confirmation_date: WorkerBidView.datetime_format,
        TechnicalRequest.reopen_deadline_date: WorkerBidView.datetime_format,
    }

    column_formatters_detail = column_formatters
    form_converter = TechnicalRequestConverter

    column_default_sort = "state"
    form_ajax_refs = {
        "repairman": {
            "fields": ("l_name", "f_name", "o_name"),
            "order_by": "l_name",
        },
        "department": {
            "fields": ("name",),
            "order_by": "name",
        },
        "problem": {
            "fields": ("problem_name",),
            "order_by": "name",
        },
        "appraiser": {
            "fields": ("l_name", "f_name", "o_name"),
            "order_by": "l_name",
        },
        "worker": {
            "fields": ("l_name", "f_name", "o_name"),
            "order_by": "l_name",
        },
    }

    def sort_query(self, stmt, request: Request):
        from sqlalchemy import asc, desc

        sort_by = request.query_params.get("sortBy", None)
        sort = request.query_params.get("sort", "asc")

        if sort_by:
            sort_fields = [(sort_by, sort == "desc")]
        else:
            sort_fields = self._get_default_sort()

        for sort_field, is_desc in sort_fields:
            model = self.model

            if sort_field == "repairman" or sort_field == "department":
                sort_field = sort_field + "_id"

            if is_desc:
                stmt = stmt.order_by(desc(getattr(model, sort_field)))
            else:
                stmt = stmt.order_by(asc(getattr(model, sort_field)))

        return stmt


class WorkTimeAdminView(ModelView, model=WorkTime):
    name = "Явка"
    name_plural = "Явки"

    can_create = False
    can_edit = False
    can_export = False

    column_list = [
        WorkTime.id,
        WorkTime.worker,
        WorkTime.post,
        WorkTime.department,
        WorkTime.company,
        WorkTime.work_begin,
        WorkTime.work_end,
        WorkTime.work_duration,
        WorkTime.day,
        WorkTime.rating,
        WorkTime.fine,
        WorkTime.salary,
    ]

    column_sortable_list = [
        WorkTime.id,
    ]

    column_labels = {
        WorkTime.worker: "Сотрудник",
        WorkTime.post: "Должность",
        WorkTime.department: "Департамент",
        WorkTime.company: "Компания",
        WorkTime.work_begin: "Начало работы",
        WorkTime.work_end: "Конец работы",
        WorkTime.work_duration: "Продолжительность (часы и доли часа)",
        WorkTime.day: "День",
        WorkTime.rating: "Рейтинг",
        WorkTime.fine: "Штраф",
        WorkTime.salary: "Зарплата",
    }


class AccountLoginsView(ModelView, model=AccountLogins):
    name = "Логин"
    name_plural = "Логины"

    can_create = True
    can_edit = True
    can_export = False

    column_list = [
        AccountLogins.id,
        AccountLogins.worker,
        AccountLogins.cop_mail_login,
        AccountLogins.liko_login,
        AccountLogins.bitrix_login,
        AccountLogins.pyrus_login,
        AccountLogins.check_office_login,
        AccountLogins.pbi_login,
    ]

    column_details_exclude_list = [AccountLogins.worker_id]

    column_sortable_list = [
        AccountLogins.id,
    ]

    column_labels = {
        AccountLogins.id: "id",
        AccountLogins.worker: "Сотрудник",
        AccountLogins.cop_mail_login: "Корпоративная почта",
        AccountLogins.liko_login: "Iiko",
        AccountLogins.bitrix_login: "Bitrix",
        AccountLogins.pyrus_login: "Pyrus",
        AccountLogins.check_office_login: "CheckOffice",
        AccountLogins.pbi_login: "PBI",
    }

    form_ajax_refs = {
        "worker": {
            "fields": ("l_name", "f_name", "o_name"),
            "order_by": "l_name",
        },
    }

    @staticmethod
    def search_query(stmt: Select, term):
        workers_id = select(Worker.id).filter(
            or_(
                Worker.f_name.ilike(f"%{term}%"),
                Worker.l_name.ilike(f"%{term}%"),
                Worker.o_name.ilike(f"%{term}%"),
            )
        )

        return select(AccountLogins).filter(
            AccountLogins.worker_id.in_(workers_id),
        )

    column_searchable_list = [
        "Фамилия",
        "Имя",
        "Отчество",
    ]


class MaterialValuesView(ModelView, model=MaterialValues):
    name = "Материальная ценность"
    name_plural = "Материальные ценности"

    can_create = True
    can_edit = True
    can_export = False

    column_list = [
        MaterialValues.id,
        MaterialValues.worker,
        MaterialValues.item,
        MaterialValues.price,
        MaterialValues.inventory_number,
        MaterialValues.issue_date,
        MaterialValues.return_date,
    ]

    column_details_exclude_list = [MaterialValues.worker_id]

    column_sortable_list = [
        MaterialValues.id,
        MaterialValues.item,
        MaterialValues.price,
        MaterialValues.inventory_number,
        MaterialValues.return_date,
        MaterialValues.issue_date,
    ]

    @staticmethod
    def search_query(stmt: Select, term):
        workers_id = select(Worker.id).filter(
            or_(
                Worker.f_name.ilike(f"%{term}%"),
                Worker.l_name.ilike(f"%{term}%"),
                Worker.o_name.ilike(f"%{term}%"),
            )
        )

        return select(MaterialValues).filter(
            or_(
                MaterialValues.worker_id.in_(workers_id),
                MaterialValues.item.ilike(f"%{term}%"),
                MaterialValues.inventory_number.ilike(f"%{term}%"),
            )
        )

    column_searchable_list = [
        "Фамилия",
        "Имя",
        "Отчество",
        MaterialValues.item,
        MaterialValues.inventory_number,
    ]

    column_labels = {
        MaterialValues.worker: "Сотрудник",
        MaterialValues.item: "Предмет",
        MaterialValues.quanity: "Количество",
        MaterialValues.price: "Цена",
        MaterialValues.inventory_number: "Инвентаризационный номер",
        MaterialValues.issue_date: "Дата выдачи",
        MaterialValues.return_date: "Дата возврата",
    }

    form_ajax_refs = {
        "worker": {
            "fields": ("l_name", "f_name", "o_name"),
            "order_by": "l_name",
        },
    }


class SubordinationView(ModelView, model=Subordination):
    name = "Субординация"
    name_plural = "Субординация"

    can_create = True
    can_edit = False
    can_export = False

    column_list = [
        Subordination.id,
        Subordination.chief,
        Subordination.employee,
    ]
    column_details_exclude_list = [
        Subordination.employee_id,
        Subordination.chief_id,
    ]

    column_sortable_list = [
        Subordination.id,
    ]

    @staticmethod
    def search_query(stmt: Select, term):
        workers_id = select(Worker.id).filter(
            or_(
                Worker.f_name.ilike(f"%{term}%"),
                Worker.l_name.ilike(f"%{term}%"),
                Worker.o_name.ilike(f"%{term}%"),
            )
        )

        return select(Subordination).filter(
            or_(
                Subordination.chief_id.in_(workers_id),
                Subordination.employee_id.in_(workers_id),
            )
        )

    column_searchable_list = [
        "Фамилия",
        "Имя",
        "Отчество",
    ]

    column_labels = {
        Subordination.chief: "Руководитель",
        Subordination.employee: "Сотрудник",
        Subordination.id: "id",
    }

    form_ajax_refs = {
        "chief": {
            "fields": ("l_name", "f_name", "o_name"),
            "order_by": "l_name",
        },
        "employee": {
            "fields": ("l_name", "f_name", "o_name"),
            "order_by": "l_name",
        },
    }


class WorkerFingerprintView(ModelView, model=WorkerFingerprint):
    name = "Отпечатки рабочих"
    name_plural = "Отпечатки рабочих"

    can_create = True
    can_edit = True
    can_export = False

    column_list = [
        WorkerFingerprint.id,
        WorkerFingerprint.worker_id,
        WorkerFingerprint.department_id,
        WorkerFingerprint.department_hex,
        WorkerFingerprint.cell_number,
        WorkerFingerprint.rfid_card,
    ]

    column_sortable_list = [
        WorkerFingerprint.id,
        WorkerFingerprint.worker_id,
    ]

    column_labels = {
        WorkerFingerprint.worker_id: "Сотрудники",
        WorkerFingerprint.department_id: "Департамент",
        WorkerFingerprint.department_hex: "Номер СУКД устройства",
        WorkerFingerprint.cell_number: "Номер ячейки",
        WorkerFingerprint.rfid_card: "РФИД карты",
    }


class FingerprintAttemptView(ModelView, model=FingerprintAttempt):
    name = "Попытки авторизаций на СКУДЕ"
    name_plural = "Попытки авторизаций на СКУДЕ"

    can_create = False
    can_edit = False
    can_export = False

    column_list = [
        FingerprintAttempt.id,
        FingerprintAttempt.worker_finger_or_card,
        FingerprintAttempt.department,
        FingerprintAttempt.event_dttm,
    ]

    column_sortable_list = [
        FingerprintAttempt.id,
        FingerprintAttempt.event_dttm,
    ]

    column_labels = {
        FingerprintAttempt.worker_finger_or_card: "Карта или номер ячейки",
        FingerprintAttempt.department: "Номер устройства СКУД",
        FingerprintAttempt.event_dttm: "Время авторизации",
    }
