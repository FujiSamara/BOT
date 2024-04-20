# sqladmin shemas
from io import BytesIO
from typing import Any, List
from sqladmin import ModelView
from starlette.responses import StreamingResponse
from db.models import *
from xlsxwriter import Workbook
from settings import get_settings
from pathlib import Path
from bot.kb import payment_type_dict

class PostView(ModelView, model=Post):
    column_list = [Post.id, Post.name, Post.level]
    column_searchable_list = [Post.name, Post.level]
    form_excluded_columns = [Post.workers]
    can_export = False

    name_plural = "Должности"
    name = "Должность"
    column_labels = {Post.name: "Название", Post.level: "Уровень доступа", Post.workers: "Работники"}
    
class CompanyView(ModelView, model=Company):
    column_list = [Company.id, Company.name]
    column_searchable_list = [Company.name]
    form_columns = [Company.name]
    can_export = False

    name_plural = "Компании"
    name = "Компания"
    column_labels = {Company.name: "Название", Company.departments: "Производства"}
    
class DepartmentView(ModelView, model=Department):
    column_list = [Department.id, Department.name]
    column_searchable_list = [Department.name]
    column_details_exclude_list = [Department.company_id]
    form_excluded_columns = [Department.workers, Department.bids]
    can_export = False

    name_plural = "Производства"
    name = "Производство"
    column_labels = {
        Department.name: "Название",
        Department.address: "Адрес",
        Department.workers: "Работники",
        Department.bids: "Заявки",
        Department.company: "Компания",
    }

    form_ajax_refs = {
        "company": {
            "fields": ("name", ),
            "order_by": "name",
        }
    }

class WorkerView(ModelView, model=Worker):
    column_searchable_list = [Worker.f_name, Worker.l_name, Worker.o_name, Worker.phone_number]
    column_list = [Worker.f_name, Worker.l_name, Worker.o_name, Worker.phone_number]
    column_details_exclude_list = [Worker.department_id, Worker.post_id]
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
    }

    form_columns = [
        Worker.f_name,
        Worker.l_name,
        Worker.o_name,
        Worker.phone_number,
        Worker.department,
        Worker.post,
        Worker.b_date
    ]

    form_ajax_refs = {
        "department": {
            "fields": ("name", ),
            "order_by": "name",
        },
        "post": {
            "fields": ("name", ),
            "order_by": "name",
        }
    }

class BidView(ModelView, model=Bid):
    details_template = "bid_details.html"
    list_template = "bid_list.html"

    can_create = False
    can_edit = False

    column_list = [
        Bid.id,
        Bid.create_date,
        Bid.worker,
        Bid.amount,
        Bid.payment_type,
        Bid.department,
        Bid.purpose,
        Bid.document,
        Bid.agreement,
        Bid.need_document,
        Bid.urgently,
        Bid.comment,
        Bid.kru_state,
        Bid.owner_state,
        Bid.accountant_cash_state,
        Bid.accountant_card_state,
        Bid.teller_cash_state,
        Bid.teller_card_state
    ]

    column_details_list = column_list

    @staticmethod
    def datetime_format(value, format="%H:%M %d-%m-%y"):
        return value.strftime(format)
    
    @staticmethod
    def file_format(inst, columm):
        value = getattr(inst, columm)
        proto = "http"
        host = get_settings().host
        port = get_settings().port
        if get_settings().ssl_certfile:
            proto = "https"

        filename = Path(value).name

        return {"filename": filename, "href": f"{proto}://{host}:{port}/admin/download?path={value}"}

    @staticmethod
    def payment_type_format(inst, column):
        value = getattr(inst, "payment_type")

        return payment_type_dict.get(value)

    @staticmethod
    def approval_status_format(inst, columm):
        value = getattr(inst, columm)

        if value == ApprovalStatus.approved:
            return "Согласовано"
        elif value == ApprovalStatus.pending:
            return "Ожидает поступления"
        elif value == ApprovalStatus.pending_approval:
            return "Ожидает согласования"
        elif value == ApprovalStatus.denied:
            return "Отклонено"
        elif value == ApprovalStatus.skipped:
            return "Пропущено"

    
    column_type_formatters = {
        datetime.datetime: datetime_format
    }
    column_formatters = {
       Bid.kru_state: approval_status_format,
       Bid.owner_state: approval_status_format,
       Bid.accountant_card_state: approval_status_format,
       Bid.accountant_cash_state: approval_status_format,
       Bid.teller_card_state: approval_status_format,
       Bid.teller_cash_state: approval_status_format,
       Bid.document: file_format,
       Bid.payment_type: payment_type_format
    }
    column_formatters_detail = column_formatters

    async def export_data(self, data: List[Any], export_type: str = "csv") -> StreamingResponse:
        '''
        Overrides `ModelView.export_date` to return `xlsx` tables instead `csv`.
        '''
        CELL_LENGTH = 18

        output = BytesIO()
        workbook = Workbook(output)
        worksheet = workbook.add_worksheet()
        worksheet.set_column(0, len(self._export_prop_names), CELL_LENGTH)
        worksheet.write_row(0, 0, self._export_prop_names)
        for index, elem in enumerate(data):
            vals = []
            for name in self._export_prop_names:
                val = await self.get_prop_value(elem, name)
                if type(val) == datetime.datetime:
                    val = BidView.datetime_format(val)
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
       Bid.create_date: "Дата создания",
       Bid.department: "Производство",
       Bid.need_document: "Необходимость документа, подтверждающего оплату",
       Bid.payment_type: "Тип оплаты",
       Bid.purpose: "Цель платежа",
       Bid.urgently: "Срочная",
       Bid.worker: "Работник",
       Bid.document: "Подтверждающий документ",
       Bid.kru_state: "КРУ",
       Bid.owner_state: "Собственник",
       Bid.accountant_card_state: "Бухгалтер безнал.",
       Bid.accountant_cash_state: "Бухгалтер нал.",
       Bid.teller_card_state: "Кассир безнал.",
       Bid.teller_cash_state: "Кассир нал.",
    }

    form_ajax_refs = {
        "department": {
            "fields": ("name", ),
            "order_by": "name",
        },
        "worker": {
            "fields": ("f_name", ),
            "order_by": "l_name",
        }
    }