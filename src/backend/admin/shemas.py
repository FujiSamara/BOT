# sqladmin shemas
from sqladmin import ModelView
from db.models import *

class PostView(ModelView, model=Post):
    column_list = [Post.id, Post.name, Post.level]
    column_searchable_list = [Post.name, Post.level]
    form_excluded_columns = [Post.workers]

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
    column_searchable_list = [Worker.f_name, Worker.l_name, Worker.o_name, Worker.phone_number]
    column_list = [Worker.f_name, Worker.l_name, Worker.o_name, Worker.phone_number]
    column_details_exclude_list = [Worker.department_id, Worker.post_id]

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
