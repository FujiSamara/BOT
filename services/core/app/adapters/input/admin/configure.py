from app.adapters.input.admin.schemas import (
    DepartmentView,
    CompanyView,
    GroupView,
    PostScopeView,
    PostView,
    WorkerView,
    WorkerBidView,
    TechnicalRequestView,
    WorkTimeAdminView,
    AccountLoginsView,
    MaterialValuesView,
    SubordinationView,
    WorkerFingerprintView,
    FingerprintAttemptView,
    WorkerDocumentView,
    WorkerChildrenView,
    AuthClientView,
    AuthClientScopeView,
)


# Routers
from app.adapters.input.admin.admin import FujiAdmin


def configure(admin: FujiAdmin):
    """Configure fast api admin app."""
    admin.add_view(DepartmentView)
    admin.add_view(CompanyView)
    admin.add_view(GroupView)
    admin.add_view(PostScopeView)
    admin.add_view(PostView)
    admin.add_view(WorkerView)
    admin.add_view(WorkerDocumentView)
    admin.add_view(WorkerChildrenView)
    admin.add_view(WorkerBidView)
    admin.add_view(TechnicalRequestView)
    admin.add_view(WorkTimeAdminView)
    admin.add_view(AccountLoginsView)
    admin.add_view(MaterialValuesView)
    admin.add_view(SubordinationView)
    admin.add_view(WorkerFingerprintView)
    admin.add_view(FingerprintAttemptView)
    admin.add_view(AuthClientView)
    admin.add_view(AuthClientScopeView)
