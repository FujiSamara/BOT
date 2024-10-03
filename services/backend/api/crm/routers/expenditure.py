from fastapi import Security
from fastapi.routing import APIRouter

from db import service
from db.schemas import ExpenditureSchema, TalbeInfoSchema, QuerySchema

from api.auth import User, authorize


router = APIRouter()


@router.post("/page/info")
async def get_pages_info(
    query: QuerySchema,
    records_per_page: int = 15,
    _: User = Security(authorize, scopes=["crm_expenditure"]),
) -> TalbeInfoSchema:
    record_count = service.get_expenditure_count(query)
    all_record_count = service.get_expenditure_count(QuerySchema())
    page_count = (record_count + records_per_page - 1) // records_per_page

    return TalbeInfoSchema(
        record_count=record_count,
        page_count=page_count,
        all_record_count=all_record_count,
    )


@router.post("/page/{page}")
async def get_expenditures(
    page: int,
    query: QuerySchema,
    records_per_page: int = 15,
    _: User = Security(authorize, scopes=["crm_expenditure"]),
) -> list[ExpenditureSchema]:
    return service.get_expenditures_at_page(page, records_per_page, query)


@router.get("/find")
async def find_expenditures(
    record: str, _: User = Security(authorize, scopes=["authenticated"])
) -> list[ExpenditureSchema]:
    """Finds expenditures by given `record`.

    Search is carried out by name and chapter.
    """
    return service.find_expenditures(record)


@router.post("/")
async def create_expenditure(
    schema: ExpenditureSchema,
    user: User = Security(authorize, scopes=["crm_expenditure"]),
) -> None:
    schema.creator = service.get_worker_by_phone_number(user.username)
    service.create_expenditure(schema)


@router.delete("/{id}")
async def delete_expenditure(
    id: int, _: User = Security(authorize, scopes=["crm_expenditure"])
) -> None:
    service.remove_expenditure(id)


@router.patch("/")
async def update_expenditure(
    schema: ExpenditureSchema,
    _: User = Security(authorize, scopes=["crm_expenditure"]),
) -> None:
    service.update_expenditure(schema)
