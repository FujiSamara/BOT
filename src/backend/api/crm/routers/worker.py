from fastapi.routing import APIRouter

from db import service
from db.schemas import WorkerSchema


router = APIRouter()


@router.get("/find")
async def find_workers(record: str) -> list[WorkerSchema]:
    """Finds workers by given `record`.

    Search is carried out by f_name, l_name, o_name.
    """
    return service.find_workers(record)
