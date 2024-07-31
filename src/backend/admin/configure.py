from admin.schemas import (
    DepartmentView,
    CompanyView,
    PostView,
    WorkerView,
    WorkerBidView,
)


# Routers
from admin.admin import FujiAdmin


def configure(admin: FujiAdmin):
    """Configure fast api admin app."""
    admin.add_view(DepartmentView)
    admin.add_view(CompanyView)
    admin.add_view(PostView)
    admin.add_view(WorkerView)
    admin.add_view(WorkerBidView)
