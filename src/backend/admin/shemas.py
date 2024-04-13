# sqladmin shemas
from sqladmin import ModelView
from db.models import *


class RoleView(ModelView, model=Role):
    column_list = [Role.id, Role.name, Role.level]
    column_searchable_list = [Role.name]
    column_details_exclude_list = [Role.posts]
    form_columns = [Role.name, Role.level]

class PostView(ModelView, model=Post):
    column_list = [Post.id, Post.name]
    column_searchable_list = [Post.name]
    form_excluded_columns = [Post.workers]

    form_ajax_refs = {
        "role": {
            "fields": ("name",),
            "order_by": "name",
        }
    }

class CompanyView(ModelView, model=Company):
    column_list = [Company.id, Company.name]
    column_searchable_list = [Company.name]
    form_columns = [Company.name]
    name_plural = "Companies"
    
class EnterpriseView(ModelView, model=Department):
    column_list = [Department.id, Department.name]
    column_searchable_list = [Department.name]
    column_details_exclude_list = [Department.company_id]
    form_excluded_columns = [Department.workers]

    form_ajax_refs = {
        "company": {
            "fields": ("name", ),
            "order_by": "name",
        }
    }

class EmployeeView(ModelView, model=Worker):
    column_searchable_list = [Worker.worker_f_name, Worker.worker_l_name, Worker.worker_o_name, Worker.phone_number]
    column_list = [Worker.worker_f_name, Worker.worker_l_name, Worker.worker_o_name, Worker.phone_number]
    column_details_exclude_list = [Worker.department_id, Worker.post_id]

    form_columns = [
        Worker.worker_f_name,
        Worker.worker_l_name,
        Worker.worker_o_name,
        Worker.phone_number,
        Worker.department,
        Worker.post
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
