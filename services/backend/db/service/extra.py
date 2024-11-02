from settings import get_settings
import db.orm as orm
from db.models import (
    Department,
    FujiScope,
    Post,
    Worker,
    Company,
)
from db.schemas import (
    PostSchema,
    WorkerSchema,
    DepartmentSchema,
    FileOutSchema,
    AccountLoginsSchema,
    MaterialValuesSchema,
)
import logging
from typing import Optional


def get_worker_by_telegram_id(id: str) -> Optional[WorkerSchema]:
    """
    Returns worker by his telegram id.
    Return `None`, if worker doesn't exits.
    """
    return orm.find_worker_by_column(Worker.telegram_id, id)


def get_workers_by_scope(scope: FujiScope) -> list[WorkerSchema]:
    """
    Returns all workers in database by `scope`.
    """
    return orm.get_workers_with_scope(scope)


def get_workers_in_department_by_scope(
    scope: FujiScope, department_id: int
) -> list[WorkerSchema]:
    """
    Returns all workers in department in database by `scope`.
    """

    return orm.get_workers_in_department_with_scope(scope, department_id)


def get_worker_department_by_telegram_id(id: str) -> DepartmentSchema:
    """
    Returns worker department by his telegram id.

    If worker not exist return `None`.
    """
    worker = orm.find_worker_by_column(Worker.telegram_id, id)

    if not worker:
        return None

    return orm.find_department_by_column(Department.id, worker.department.id)


def update_worker_tg_id_by_number(number: str, tg_id: int) -> bool:
    """
    Finds worker by his phone number and sets him telegram id.

    Returns `True`, if worker found, `False` otherwise.
    """
    worker = orm.find_worker_by_column(Worker.phone_number, number)
    if not worker:
        return False

    worker.telegram_id = tg_id
    try:
        orm.update_worker(worker)
    except Exception as e:
        logging.getLogger("uvicorn.error").error(f"update_worker error: {e}")
        return False
    return True


def get_departments_names(_all: bool = False) -> list[str]:
    """
    Returns all existed departments names.
    """
    departments_raw = orm.get_departments_columns(Department.name)
    result = [column[0] for column in departments_raw]
    try:
        if not _all:
            result.remove("Нет производства")
    except Exception:
        logging.getLogger("uvicorn.error").error(
            "Department with name 'Нет производства' wasn't found"
        )
    finally:
        return result


def get_departments_ids() -> list[int]:
    """
    Returns all existed departments ids.
    """
    departments_raw = orm.get_departments_columns(Department.id)
    result = [column[0] for column in departments_raw]
    return result


def get_worker_by_phone_number(number: str) -> WorkerSchema | None:
    """
    Finds worker by his phone number.
    """
    return orm.find_worker_by_column(Worker.phone_number, number)


def get_worker_by_id(id: int) -> WorkerSchema:
    """
    Returns worker in database with `id` at column.

    If worker not exist return `None`.
    """
    return orm.find_worker_by_column(Worker.id, id)


def get_chef_by_department_id(id: int) -> WorkerSchema:
    """
    Return first owner in database by owner department`id`.

    If record not exist returns `None`.
    """
    chef_level = 6

    owners = orm.get_workers_with_post_by_columns(
        [Worker.department_id, Post.level], [id, chef_level]
    )
    if len(owners) > 0:
        return owners[0]


def get_posts_names() -> list[str]:
    """Returns all posts names in db."""
    return [post.name for post in orm.get_posts()]


def get_file_data(filename: str, mode: str = "sqladmin") -> FileOutSchema:
    """Returns file `FileSchema` with file href and name.
    - `mode`  Specifies file request source.
    """
    proto = "http"
    host = get_settings().domain
    port = get_settings().port
    if get_settings().ssl_certfile:
        proto = "https"

    source: str = ""

    if mode == "sqladmin":
        source = "/admin"
    elif mode == "api":
        source = "/api"

    return FileOutSchema(
        name=filename, href=f"{proto}://{host}:{port}{source}/download?name={filename}"
    )


def find_workers(record: str) -> list[WorkerSchema]:
    """Finds workers by given `record`.

    Search is carried out by f_name, l_name, o_name.
    """
    return orm.find_workers_by_name(record)


def find_posts(record: str) -> list[PostSchema]:
    """Finds posts by given `record`."""
    return orm.find_posts_by_name(record)


def find_department_by_name(record: str) -> list[DepartmentSchema]:
    """Finds departments by given `record`.

    Search is carried out by name.
    """
    return orm.find_departments_by_name(record)


def get_groups_names() -> list[str]:
    """Returns list of all groups names in db"""
    groups = orm.get_groups()
    return [group.name for group in groups]


def get_logins(worker_id) -> Optional[AccountLoginsSchema]:
    logins = orm.get_logins(worker_id=worker_id)
    if not logins:
        return None
    return logins


def get_worker_chief(telegram_id: int) -> Optional[WorkerSchema]:
    worker_id = get_worker_by_telegram_id(telegram_id).id
    chief = orm.get_subordination_chief(worker_id=worker_id)
    if chief is None:
        return None
    return chief


def get_material_values(telegram_id: int) -> list[MaterialValuesSchema]:
    worker_id = get_worker_by_telegram_id(telegram_id).id
    material_values = orm.get_material_values(worker_id=worker_id)
    return material_values


def get_material_value_by_inventory_number(
    inventory_number: int,
) -> MaterialValuesSchema:
    material_value = orm.get_material_value_by_inventory_number(
        inventory_number=inventory_number
    )
    return material_value


def set_department_for_worker(telegram_id: int, department_name: str) -> bool:
    """Change department for worker"""
    if orm.set_department_for_worker(telegram_id, department_name):
        return True
    logging.getLogger("uvicorn.error").error(
        f"The employee's department could not be changed. TG id: {telegram_id}. Department_name: {department_name}"
    )
    return False


def get_tellers_cash_for_department(department_id: int) -> list[Worker]:
    """:return: all tellers cash in department with id `department_id`."""
    return orm.get_tellers_cash_in_department(department_id)


def get_companies_names():
    return orm.get_companies_names()


def set_tellers_cash_department() -> list[WorkerSchema]:
    """"""
    company_name = "Нет компании"
    department_name = "Нет производства"
    if company_name not in get_companies_names():
        orm.create_company(company_name=company_name)
        if department_name in get_departments_names(_all=True):
            orm.update_company_for_department(
                company_name=company_name,
                department_name=department_name,
            )
        else:
            company = orm.get_companys({Company.name: company_name})[0]
            orm.create_department(name=department_name, address=None, company=company)
    elif department_name not in get_departments_names(_all=True):
        company = orm.get_companys({Company.name: company_name})[0]
        orm.create_department(name=department_name, address=None, company=company)

    return orm.set_tellers_cash_department()
