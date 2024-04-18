from admin.schemas import DepartmentView, CompanyView, PostView, WorkerView, BidView

# Routers
from sqladmin import Admin

def configure(admin: Admin):
    '''Configure fast api admin app.
    '''
    admin.add_view(DepartmentView)
    admin.add_view(CompanyView)
    admin.add_view(PostView)
    admin.add_view(WorkerView)
    admin.add_view(BidView)