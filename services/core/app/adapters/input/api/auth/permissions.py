from fastapi.security import OAuth2PasswordBearer
from app.database.models import FujiScope

_scopes = {
    "admin": "Full access",
    # CRM
    "authenticated": "Authenticated in crm",
    "crm_bid": "Can view bid crm page",
    "crm_budget": "Can view budget crm page",
    "crm_expenditure": "Can view expenditure crm page",
    "crm_fac_bid": "Can view fac bid crm page",
    "crm_cc_bid": "Can view cc bid crm page",
    "crm_paralegal_bid": "Can view cc supervisor bid crm page",
}


def _to_auth_scope(fuji_scope: FujiScope) -> str:
    """Converts `FujiScopes` to auth str scope."""
    return fuji_scope.name


def _to_fuji_scope(scope: str) -> FujiScope:
    """Converts auth str scope to `FujiScopes`."""
    return FujiScope[scope]


_oauth2_schema = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes=_scopes,
)
