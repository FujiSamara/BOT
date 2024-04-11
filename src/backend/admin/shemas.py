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
    form_excluded_columns = [Post.employees]

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
    
class EnterpriseView(ModelView, model=Enterprise):
    column_list = [Enterprise.id, Enterprise.name]
    column_searchable_list = [Enterprise.name]
    column_details_exclude_list = [Enterprise.company_id]
    form_excluded_columns = [Enterprise.employees]

    form_ajax_refs = {
        "company": {
            "fields": ("name", ),
            "order_by": "name",
        }
    }

class EmployeeView(ModelView, model=Employee):
    column_searchable_list = [Employee.name, Employee.surname, Employee.patronymic, Employee.phone_number]
    column_list = [Employee.name, Employee.surname, Employee.patronymic, Employee.phone_number]
    column_details_exclude_list = [Employee.enterprise_id, Employee.post_id]

    form_columns = [
        Employee.name,
        Employee.surname,
        Employee.patronymic,
        Employee.phone_number,
        Employee.enterprise,
        Employee.post
    ]

    form_ajax_refs = {
        "enterprise": {
            "fields": ("name", ),
            "order_by": "name",
        },
        "post": {
            "fields": ("name", ),
            "order_by": "name",
        }
    }
