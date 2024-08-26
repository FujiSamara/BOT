# sqladmin shemas
from fastapi import Request
from fastapi.responses import RedirectResponse
from sqladmin import ModelView, action
from db.models import (
    PostScope,
    Worker,
    Company,
    Department,
    Post,
    WorkerBid,
    WorkerBidDocument,
    ApprovalStatus,
    Gender,
)
from bot.kb import payment_type_dict, approval_status_dict
from db.schemas import FileSchema
from db import service
from api.auth import encrypt_password


class PostScopeView(ModelView, model=PostScope):
    column_list = [PostScope.post, PostScope.scope]
    column_searchable_list = [PostScope.scope]
    form_columns = [PostScope.scope, PostScope.post]
    column_details_exclude_list = [PostScope.post_id, PostScope.id]
    can_export = False
    can_edit = False

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
        Post.workers: "Работники",
        Post.salary: "Зарплата",
        Post.scopes: "Доступы",
    }


class CompanyView(ModelView, model=Company):
    column_list = [Company.id, Company.name]
    column_details_exclude_list = [
        Company.biosmart_strid,
        Company.bs_import,
        Company.work_times,
    ]
    column_searchable_list = [Company.name]
    form_columns = [Company.name]
    can_export = False

    name_plural = "Компании"
    name = "Компания"
    column_labels = {
        Company.name: "Название",
        Company.departments: "Производства",
        Company.workers: "Работники",
        Company.bs_import_error: "Ошибка импорта из биосмарт",
    }


class DepartmentView(ModelView, model=Department):
    column_list = [Department.id, Department.name]
    column_searchable_list = [Department.name]
    column_details_exclude_list = [
        Department.company_id,
        Department.bs_import,
        Department.bs_import_error_text,
        Department.work_times,
        Department.biosmart_strid,
        Department.workers_bids,
        Department.bids,
        Department.delivery_manager_id,
        Department.territorial_manager_id,
        Department.territorial_director_id,
        Department.territorial_brand_chef_id,
        Department.technical_requests,
        Department.budget_records,
        Department.technician_id,
        Department.electrician_id,
        Department.chief_technician_id,
    ]
    form_excluded_columns = [
        Department.workers,
        Department.bids,
        Department.bs_import,
        Department.bs_import_error_text,
        Department.work_times,
        Department.bs_import_error,
        Department.biosmart_strid,
        Department.workers_bids,
        Department.technical_requests,
        Department.budget_records,
    ]
    can_export = False

    name_plural = "Производства"
    name = "Производство"
    column_labels = {
        Department.name: "Название",
        Department.address: "Адрес",
        Department.workers: "Работники",
        Department.bids: "Заявки",
        Department.company: "Компания",
        Department.bs_import_error: "Ошибка импорта из биосмарт",
        Department.type: "Формат",
        Department.city: "Город",
        Department.opening_date: "Дата открытия",
        Department.closing_date: "Дата закрытия",
        Department.area: "Общая площадь",
        Department.territorial_manager: "Территориальный управляющий",
        Department.territorial_brand_chef: "Территориальный брендшеф",
        Department.delivery_manager: "Менеджер доставки",
        Department.territorial_director: "Территориальный директор",
        Department.chief_technician: "Главный техник",
        Department.technician: "Техник",
        Department.electrician: "Электрик",
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


class WorkerView(ModelView, model=Worker):
    column_searchable_list = [
        Worker.f_name,
        Worker.l_name,
        Worker.o_name,
        Worker.phone_number,
    ]
    column_list = [Worker.f_name, Worker.l_name, Worker.o_name, Worker.phone_number]
    column_details_exclude_list = [
        Worker.department_id,
        Worker.post_id,
        Worker.bids,
        Worker.work_times,
        Worker.company_id,
        Worker.biosmart_strid,
        Worker.bs_import,
        Worker.bs_import_error_text,
        Worker.worker_bids,
        Worker.facs,
        Worker.ccs,
        Worker.cc_supervisors,
        Worker.password,
        Worker.repairman_technical_requests,
        Worker.worker_technical_requests,
        Worker.territorial_manager_technical_requests,
        Worker.expenditures,
    ]
    can_export = False

    name_plural = "Работники"
    name = "Работник"
    column_labels = {
        Worker.f_name: "Имя",
        Worker.l_name: "Фамилия",
        Worker.o_name: "Отчество",
        Worker.department: "Производство",
        Worker.post: "Должность",
        Worker.b_date: "Дата рождения",
        Worker.bids: "Заявки",
        Worker.phone_number: "Номер телефона",
        Worker.company: "Компания",
        Worker.telegram_id: "ID телеграмм",
        Worker.bs_import_error: "Ошибка импорта из биосмарт",
        Worker.employment_date: "Дата приема",
        Worker.dismissal_date: "Дата увольнения",
        Worker.medical_records_availability: "Наличие медицинской книжки",
        Worker.gender: "Пол",
        Worker.citizenship: "Гражданство",
        Worker.can_use_crm: "Может использовать CRM",
        Worker.password: "Пароль",
    }

    form_columns = [
        Worker.f_name,
        Worker.l_name,
        Worker.o_name,
        Worker.phone_number,
        Worker.department,
        Worker.telegram_id,
        Worker.post,
        Worker.b_date,
        Worker.employment_date,
        Worker.dismissal_date,
        Worker.medical_records_availability,
        Worker.gender,
        Worker.citizenship,
        Worker.can_use_crm,
        Worker.password,
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
    }

    @staticmethod
    def gender_format(inst, columm):
        value = getattr(inst, columm)

        if value == Gender.man:
            return "Мужчина"
        else:
            return "Женщина"

    async def on_model_change(self, data, model, is_created, request):
        if "password" in data:
            data["password"] = encrypt_password(data["password"])

    column_formatters = {Worker.gender: gender_format}
    column_formatters_detail = column_formatters


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
        WorkerBid.passport: "Паспорт",
        WorkerBid.state: "Статус",
        WorkerBid.create_date: "Дата создания",
        WorkerBid.comment: "Комментарий",
    }

    column_list = [
        WorkerBid.id,
        WorkerBid.create_date,
        WorkerBid.l_name,
        WorkerBid.f_name,
        WorkerBid.o_name,
        WorkerBid.post,
        WorkerBid.department,
        WorkerBid.state,
        WorkerBid.comment,
    ]

    column_details_list = [
        WorkerBid.id,
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
    ]

    column_searchable_list = [WorkerBid.f_name, WorkerBid.l_name, WorkerBid.o_name]

    column_sortable_list = [
        WorkerBid.create_date,
        WorkerBid.l_name,
        WorkerBid.id,
        WorkerBid.o_name,
        WorkerBid.f_name,
    ]

    form_columns = [WorkerBid.comment]

    @staticmethod
    def datetime_format(inst, columm):
        format = "%H:%M %d.%m.%y"
        value = getattr(inst, columm)
        if value:
            return value.strftime(format)
        else:
            return "Заявка не закрыта"

    @staticmethod
    def payment_type_format(inst, column):
        value = getattr(inst, column)

        return payment_type_dict.get(value)

    @staticmethod
    def approval_status_format(inst, columm):
        value = getattr(inst, columm)

        return approval_status_dict.get(value)

    @action(
        name="approve_worker_bid",
        label="Согласовать",
        add_in_detail=True,
    )
    async def approve_worker_bid(self, request: Request):
        pk = int(request.query_params.get("pks", "").split(",")[0])
        await service.update_worker_bid_state(ApprovalStatus.approved, pk)

        return RedirectResponse(request.url_for("admin:list", identity=self.identity))

    @action(
        name="decline_worker_bid",
        label="Отказать",
        add_in_detail=True,
    )
    async def decline_worker_bid(self, request: Request):
        pk = int(request.query_params.get("pks", "").split(",")[0])
        await service.update_worker_bid_state(ApprovalStatus.denied, pk)

        return RedirectResponse(request.url_for("admin:list", identity=self.identity))

    @staticmethod
    def files_format(inst, column):
        documents: list[WorkerBidDocument] = getattr(inst, column)
        urls: list[FileSchema] = []
        for doc in documents:
            url = service.get_file_data(doc.document)
            if url:
                urls.append(url)

        return urls

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
