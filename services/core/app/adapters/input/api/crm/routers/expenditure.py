from fastapi import Security
from fastapi.routing import APIRouter

from app import services
from app.db.schemas import ExpenditureSchema, TalbeInfoSchema, QuerySchema

from app.adapters.input.api.auth import User, get_user


router = APIRouter()


@router.post("/page/info")
async def get_pages_info(
    query: QuerySchema,
    records_per_page: int = 15,
    _: User = Security(get_user, scopes=["crm_expenditure"]),
) -> TalbeInfoSchema:
    record_count = services.get_expenditure_count(query)
    all_record_count = services.get_expenditure_count(QuerySchema())
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
    _: User = Security(get_user, scopes=["crm_expenditure"]),
) -> list[ExpenditureSchema]:
    return services.get_expenditures_at_page(page, records_per_page, query)


@router.get("/find")
async def find_expenditures(
    record: str, _: User = Security(get_user, scopes=["authenticated"])
) -> list[ExpenditureSchema]:
    """Finds expenditures by given `record`.

    Search is carried out by name and chapter.
    """
    return services.find_expenditures(record)


@router.post("/")
async def create_expenditure(
    schema: ExpenditureSchema,
    user: User = Security(get_user, scopes=["crm_expenditure"]),
) -> None:
    schema.creator = services.get_worker_by_phone_number(user.username)
    services.create_expenditure(schema)


@router.delete("/{id}")
async def delete_expenditure(
    id: int, _: User = Security(get_user, scopes=["crm_expenditure"])
) -> None:
    services.remove_expenditure(id)


@router.patch("/")
async def update_expenditure(
    schema: ExpenditureSchema,
    _: User = Security(get_user, scopes=["crm_expenditure"]),
) -> None:
    services.update_expenditure(schema)
