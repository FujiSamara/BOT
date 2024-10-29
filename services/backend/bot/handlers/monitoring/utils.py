from aiogram.utils.markdown import hbold, hcode

from db.models import IncidentStage
from settings import get_settings

import db.service.equipment_status_service as es_service
import db.service.extra as ex_service
import db.schemas as schemas


def get_monitoring_list() -> str:
    """Returns multiline monitoring list."""
    statuses = es_service.get_equipment_statuses()

    sep = "\n"

    return f"""{hbold("Статусы оборудования:")}
{str.join(sep, (hcode(f'''Предприятие: {equipment_status.department.name}
Тип оборудования: {equipment_status.equipment_name}
Статус: {equipment_status.status}
''') for equipment_status in statuses))}
"""


def get_incident_short_info(incident: schemas.EquipmentIncidentSchema) -> str:
    department_name = incident.equipment_status.department.name
    date_time = incident.incident_time.strftime(get_settings().date_time_format)
    prefix = " ✅" if incident.stage == IncidentStage.processed else ""
    return f"{department_name} {date_time}{prefix}"


def get_incident_full_info(incident: schemas.EquipmentIncidentSchema) -> str:
    department_name = incident.equipment_status.department.name
    date_time = incident.incident_time.strftime(get_settings().date_time_format)
    territorial_manager = incident.equipment_status.department.territorial_manager
    territorial_manager_text = "Отсутствует"
    if territorial_manager is not None:
        territorial_manager_text = (
            f"{territorial_manager.l_name} {territorial_manager.f_name}"
        )
    tellers_cash = ex_service.get_tellers_cash_for_department(
        incident.equipment_status.department.id
    )
    status = incident.status
    equipment_name = incident.equipment_status.equipment_name
    sep = "\n"

    teller_cash_text = str.join(
        sep,
        (
            hcode(
                f"{teller_cash.l_name} {teller_cash.f_name} {teller_cash.phone_number}"
            )
            for teller_cash in tellers_cash
        ),
    )

    if len(tellers_cash) != 0:
        teller_cash_text = sep + teller_cash_text

    return f"""Производство: {hcode(department_name)}
Время инцидента: {hcode(date_time)}
Территориальный: {hcode(territorial_manager_text)}
Кассиры: {teller_cash_text}
Статус: {hcode(status)}
Оборудование: {hcode(equipment_name)}
"""


def get_incidents_history_list() -> str:
    """Returns incidents history list."""
    incidents = sorted(
        es_service.get_incidents_history(), key=lambda incident: incident.id
    )[:10]

    sep = "\n"

    return f"""{hbold("История инцидентов:")}
{str.join(sep, (hcode(f'''Предприятие: {incident.department.name}
Тип оборудования: {incident.equipment_name}
Статус: {incident.status}
''') for incident in incidents))}
"""
