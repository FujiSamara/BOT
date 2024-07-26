from fastapi import Security
from fastapi.routing import APIRouter

from db import service
from db.schemas import WorkerSchema

from api.auth import User, get_current_user


router = APIRouter()


@router.get("/find")
async def find_workers(
    record: str, _: User = Security(get_current_user, scopes=["authenticated"])
) -> list[WorkerSchema]:
    """Finds workers by given `record`.

    Search is carried out by f_name, l_name, o_name.
    """
    return service.find_workers(record)
