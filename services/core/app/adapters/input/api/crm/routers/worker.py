from fastapi import Security
from fastapi.routing import APIRouter

from app import services
from app.schemas import WorkerSchema

from app.adapters.input.api.auth import User, get_user


router = APIRouter()


@router.get("/by/name")
async def find_workers(
    name: str, _: User = Security(get_user, scopes=["authenticated"])
) -> list[WorkerSchema]:
    """Finds workers by given `name`.

    Search is carried out by f_name, l_name, o_name.
    """
    return services.find_workers(name)


@router.get("/by/phone")
async def get_worker_by_number(
    phone: str, _: User = Security(get_user, scopes=["authenticated"])
) -> WorkerSchema:
    """Finds worker by given `phone`."""
    return services.get_worker_by_phone_number(phone)
