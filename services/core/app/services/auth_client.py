from app.schemas import AuthClientSchema
from app.infra.database import orm


def get_client_by_id(id: str) -> AuthClientSchema | None:
    return orm.get_auth_client_by_id(id)
