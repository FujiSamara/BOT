from admin.shemas import RoleView, EnterpriseView, CompanyView, PostView, EmployeeView

# Routers
from sqladmin import Admin

def configure(admin: Admin):
    '''Configure fast api admin app.
    '''
    admin.add_view(RoleView)
    admin.add_view(EnterpriseView)
    admin.add_view(CompanyView)
    admin.add_view(PostView)
    admin.add_view(EmployeeView)
