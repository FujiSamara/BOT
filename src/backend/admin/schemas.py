# sqladmin shemas
from sqladmin import ModelView
from db.models import *

class PostView(ModelView, model=Post):
    column_list = [Post.id, Post.name, Post.level]
    column_searchable_list = [Post.name, Post.level]
    form_excluded_columns = [Post.workers]

    name_plural = "Должности"
    name = "Должность"
    column_labels = {Post.name: "Название", Post.level: "Уровень доступа", Post.workers: "Работники"}
    
class CompanyView(ModelView, model=Company):
    column_list = [Company.id, Company.name]
    column_searchable_list = [Company.name]
    form_columns = [Company.name]

    name_plural = "Компании"
    name = "Компания"
    column_labels = {Company.name: "Название", Company.departments: "Производства"}
    
class DepartmentView(ModelView, model=Department):
    column_list = [Department.id, Department.name]
    column_searchable_list = [Department.name]
    column_details_exclude_list = [Department.company_id]
    form_excluded_columns = [Department.workers, Department.bids]

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
    can_create=False,
    can_edit=False

    column_details_exclude_list = [Bid.worker_id, Bid.department_id]
    column_exclude_list = [Bid.worker_id, Bid.department_id]

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
       Bid.worker: "Работник"
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