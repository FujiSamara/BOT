from admin.schemas import (
    DepartmentView,
    CompanyView,
    GroupView,
    PostScopeView,
    PostView,
    WorkerView,
    WorkerBidView,
    TechnicalRequestView,
)


# Routers
from admin.admin import FujiAdmin


def configure(admin: FujiAdmin):
    """Configure fast api admin app."""
    admin.add_view(DepartmentView)
    admin.add_view(CompanyView)
    admin.add_view(GroupView)
    admin.add_view(PostScopeView)
    admin.add_view(PostView)
    admin.add_view(WorkerView)
    admin.add_view(WorkerBidView)
    admin.add_view(TechnicalRequestView)
