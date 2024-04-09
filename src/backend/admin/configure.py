from functools import lru_cache
import logging
from admin.shemas import RoleView, EnterpriseView, CompanyView

# Routers
from sqladmin import Admin

def configure(admin: Admin):
    '''Configure fast api admin app.
    '''
    admin.add_view(RoleView)
    admin.add_view(EnterpriseView)
    admin.add_view(CompanyView)



@lru_cache
def get_admin_logger() -> logging.Logger:
    return logging.getLogger("admin")
