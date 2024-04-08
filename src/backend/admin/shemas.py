# sqladmin shemas
from sqladmin import ModelView
from db.models import *

class RoleView(ModelView, model=Role):
    column_list = [Role.id, Role.name]