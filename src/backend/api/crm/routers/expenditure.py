from typing import Optional
from fastapi import Security
from fastapi.routing import APIRouter

from db import service
from db.schemas import ExpenditureSchema

from api.auth import User, get_current_user


router = APIRouter()


@router.get("/")
async def get_expenditures(
    _: User = Security(get_current_user, scopes=["crm_expenditure"]),
) -> list[ExpenditureSchema]:
    return service.get_expenditures()


@router.get("/last")
async def get_last_expenditure(
    _: User = Security(get_current_user, scopes=["crm_expenditure"]),
) -> Optional[ExpenditureSchema]:
    return service.get_last_expenditure()


@router.get("/find")
async def find_expenditures(
    record: str, _: User = Security(get_current_user, scopes=["crm_expenditure"])
) -> list[ExpenditureSchema]:
    """Finds expenditures by given `record`.

    Search is carried out by name and chapter.
    """
    return service.find_expenditures(record)


@router.post("/")
async def create_expenditure(
    schema: ExpenditureSchema,
    user: User = Security(get_current_user, scopes=["crm_expenditure"]),
) -> None:
    schema.creator = service.get_worker_by_phone_number(user.username)
    service.create_expenditure(schema)


@router.delete("/{id}")
async def delete_expenditure(
    id: int, _: User = Security(get_current_user, scopes=["crm_expenditure"])
) -> None:
    service.remove_expenditure(id)


@router.patch("/")
async def update_expenditure(
    schema: ExpenditureSchema,
    _: User = Security(get_current_user, scopes=["crm_expenditure"]),
) -> None:
    service.update_expenditure(schema)
