from fastapi import Security
from fastapi.routing import APIRouter

from db import service
from db.schemas import DepartmentSchema

from api.auth import User, get_current_user


router = APIRouter()


@router.get("/by/name")
async def find_workers(
    name: str, _: User = Security(get_current_user, scopes=["authenticated"])
) -> list[DepartmentSchema]:
    """Finds departments by given `name`.

    Search is carried out by name.
    """
    return service.find_department_by_name(name)
