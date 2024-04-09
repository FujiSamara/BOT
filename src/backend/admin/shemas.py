# sqladmin shemas
from sqladmin import ModelView
from db.models import *
import wtforms

class RoleView(ModelView, model=Role):
    column_list = [Role.id, Role.name, Role.level]

class CompanyView(ModelView, model=Company):
    column_list = [Company.id, Company.name]
    form_columns = [Company.name]
    name_plural = "Companies"


class EnterpriseView(ModelView, model=Enterprise):
    column_list = [Enterprise.id, Enterprise.name]
    column_details_list = [Enterprise.id, Enterprise.name, Enterprise.address, Enterprise.company]

    form_ajax_refs = {
        "company": {
            "fields": ("id", "name",),
            "order_by": "name",
        }
    }