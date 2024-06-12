# sqladmin shemas
import datetime
from io import BytesIO
from typing import Any, List
from fastapi import Request
from fastapi.responses import RedirectResponse
from sqladmin import ModelView, action
from starlette.responses import StreamingResponse
from db.models import (
    Bid,
    Worker,
    Company,
    Department,
    Post,
    WorkerBid,
    WorkerBidDocument,
    ApprovalStatus,
    Gender,
)
from xlsxwriter import Workbook
from bot.kb import payment_type_dict, approval_status_dict
from db.schemas import FileSchema
from db import service


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
    }

    form_columns = [
        Worker.f_name,
        Worker.l_name,
        Worker.o_name,
        Worker.phone_number,
        Worker.department,
        Worker.post,
        Worker.b_date,
        Worker.employment_date,
        Worker.dismissal_date,
        Worker.medical_records_availability,
        Worker.gender,
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

    column_formatters = {Worker.gender: gender_format}
    column_formatters_detail = column_formatters


class BidView(ModelView, model=Bid):
    details_template = "bid_details.html"
    list_template = "bid_list.html"

    can_create = False
    can_edit = False

    column_searchable_list = [
        "worker.l_name",
    ]
    column_sortable_list = [Bid.amount, Bid.create_date, Bid.close_date, Bid.id]
    column_list = [
        Bid.id,
        Bid.create_date,
        Bid.close_date,
        Bid.worker,
        Bid.amount,
        Bid.payment_type,
        Bid.department,
        Bid.purpose,
        Bid.document,
        Bid.document1,
        Bid.document2,
        Bid.agreement,
        Bid.need_document,
        Bid.urgently,
        Bid.comment,
        Bid.denying_reason,
        Bid.kru_state,
        Bid.owner_state,
        Bid.accountant_cash_state,
        Bid.accountant_card_state,
        Bid.teller_cash_state,
        Bid.teller_card_state,
    ]

    column_details_list = column_list

    @staticmethod
    def datetime_format(inst, columm):
        format = "%H:%M %d.%m.%y"
        value = getattr(inst, columm)
        if value:
            return value.strftime(format)
        else:
            return "Заявка не закрыта"

    @staticmethod
    def file_format(inst, columm):
        value = getattr(inst, columm)
        if not value:
            return None
        data = service.get_file_data(value)
        return data

    @staticmethod
    def payment_type_format(inst, column):
        value = getattr(inst, column)

        return payment_type_dict.get(value)

    @staticmethod
    def approval_status_format(inst, columm):
        value = getattr(inst, columm)

        return approval_status_dict.get(value)

    column_formatters = {
        Bid.create_date: datetime_format,
        Bid.close_date: datetime_format,
        Bid.kru_state: approval_status_format,
        Bid.owner_state: approval_status_format,
        Bid.accountant_card_state: approval_status_format,
        Bid.accountant_cash_state: approval_status_format,
        Bid.teller_card_state: approval_status_format,
        Bid.teller_cash_state: approval_status_format,
        Bid.document: file_format,
        Bid.document1: file_format,
        Bid.document2: file_format,
        Bid.payment_type: payment_type_format,
    }
    column_formatters_detail = column_formatters

    column_export_exclude_list = [
        Bid.department_id,
        Bid.worker_id,
        Bid.document,
        Bid.document1,
        Bid.document2,
    ]

    async def export_data(
        self, data: List[Any], export_type: str = "csv"
    ) -> StreamingResponse:
        """
        Overrides `ModelView.export_date`
        to return `xlsx` tables instead `csv`.
        """
        CELL_LENGTH = 18

        output = BytesIO()
        workbook = Workbook(output)
        worksheet = workbook.add_worksheet()
        worksheet.set_column(0, len(self._export_prop_names), CELL_LENGTH)
        worksheet.write_row(0, 0, [*self._export_prop_names, "Подпись"])
        for index, elem in enumerate(data):
            vals = []
            for name in self._export_prop_names:
                val = await self.get_prop_value(elem, name)
                if isinstance(val, datetime.datetime):
                    val = BidView.datetime_format(val)
                if name.split("_")[-1] == "state":
                    val = BidView.approval_status_format(elem, name)
                if name == "payment_type":
                    val = BidView.payment_type_format(elem, name)
                vals.append(str(val))

            worksheet.write_row(index + 1, 0, vals)

        workbook.close()
        output.seek(0)

        return StreamingResponse(
            content=output,
            headers={"Content-Disposition": "attachment; filename=bids.xlsx"},
        )

    name_plural = "Заявки"
    name = "Заявка"
    column_labels = {
        Bid.agreement: "Наличие соглашеия",
        Bid.amount: "Сумма",
        Bid.comment: "Комментарий",
        Bid.denying_reason: "Причина отказа",
        Bid.create_date: "Дата создания",
        Bid.close_date: "Дата закрытия",
        Bid.department: "Производство",
        Bid.need_document: "Необходимость документа, подтверждающего оплату",
        Bid.payment_type: "Тип оплаты",
        Bid.purpose: "Цель платежа",
        Bid.urgently: "Срочная",
        Bid.worker: "Работник",
        Bid.document: "Подтверждающий документ",
        Bid.document1: "Подтверждающий документ 1",
        Bid.document2: "Подтверждающий документ 2",
        Bid.kru_state: "КРУ",
        Bid.owner_state: "Собственник",
        Bid.accountant_card_state: "Бухгалтер безнал.",
        Bid.accountant_cash_state: "Бухгалтер нал.",
        Bid.teller_card_state: "Кассир безнал.",
        Bid.teller_cash_state: "Кассир нал.",
        "worker.l_name": "Фамилия работника",
    }

    form_ajax_refs = {
        "department": {
            "fields": ("name",),
            "order_by": "name",
        },
        "worker": {
            "fields": ("f_name",),
            "order_by": "l_name",
        },
    }


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
        WorkerBid.state: BidView.approval_status_format,
        WorkerBid.passport: files_format,
        WorkerBid.work_permission: files_format,
        WorkerBid.worksheet: files_format,
        WorkerBid.create_date: BidView.datetime_format,
    }

    column_formatters_detail = column_formatters
