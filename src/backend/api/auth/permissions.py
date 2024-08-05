from fastapi.security import OAuth2PasswordBearer
from db.models import FujiScope

_scopes = {
    "admin": "Full access",
    # CRM
    "authenticated": "Authenticated in crm",
    "crm_bid": "Can view bid crm page",
    "crm_budget": "Can view budget crm page",
    "crm_expenditure": "Can view expenditure crm page",
    # BOT
    "bot_bid_create": "Can view bid bot creating form",
    "bot_bid_kru": "Can view bid bot kru form",
    "bot_bid_owner": "Can view bid bot owner form",
    "bot_bid_teller_cash": "Can view bid bot teller cash form",
    "bot_bid_teller_card": "Can view bid bot teller card form",
    "bot_bid_accountant_cash": "Can view bid bot accountant cash form",
    "bot_bid_accountant_card": "Can view bid bot accountant card form",
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
