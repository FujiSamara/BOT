from aiogram.utils.markdown import hbold, hcode

import db.service.equipment_status_service as es_service


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


def get_incidents_history_list() -> str:
    """Returns incidents history list."""
    incidents = sorted(
        es_service.get_equipment_incidents(), key=lambda incident: incident.id
    )[:10]

    sep = "\n"

    return f"""{hbold("История инцидентов:")}
{str.join(sep, (hcode(f'''Предприятие: {incident.department.name}
Тип оборудования: {incident.equipment_name}
Статус: {incident.status}
''') for incident in incidents))}
"""
