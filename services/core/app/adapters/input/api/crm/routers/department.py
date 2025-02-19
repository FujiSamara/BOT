from fastapi import Security
from fastapi.routing import APIRouter

from app import services
from app.services import extra
from app.schemas import DepartmentSchema

from app.adapters.input.api.auth import User, get_user


router = APIRouter()


@router.get("/by/name")
async def find_workers(
    name: str, _: User = Security(get_user, scopes=["authenticated"])
) -> list[DepartmentSchema]:
    """Finds departments by given `name`.

    Search is carried out by name.
    """
    return services.find_department_by_name(name)


@router.get("/{id}")
async def get_department_by_id(
    id: int, _: User = Security(get_user, scopes=["authenticated"])
) -> DepartmentSchema | None:
    """Returns department by given `id`."""
    return extra.get_department_by_id(id)
