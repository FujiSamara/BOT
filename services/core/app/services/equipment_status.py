from datetime import datetime

from app.schemas import (
    DepartmentSchemaFull,
    EquipmentIncidentSchema,
    EquipmentStatusSchemaIn,
    EquipmentStatusSchema,
)
from app.infra.database.models import Department, FujiScope, IncidentStage
from app.infra.database import orm

from app.infra.logging import logger

bad_statuses = ["Не доступна"]


async def update_equipment_status(
    asterisk_id: str, equipment_status_in: EquipmentStatusSchemaIn
) -> bool:
    """Updates equipment status, adds incident if `equipment_status_in.status` is bad.

    If status not exist in database creates it.
    """

    from app.adapters.bot.handlers.utils import (
        notify_workers_by_scope,
    )

    if (
        department := orm.find_department_by_column(
            Department.asterisk_id, asterisk_id, DepartmentSchemaFull
        )
    ) is None:
        logger.warning(f"Department with asterisk id: {asterisk_id} not found.")
        return

    equipment_status = EquipmentStatusSchema(
        asterisk_id=asterisk_id,
        status=equipment_status_in.status,
        ip_address=equipment_status_in.ip_address,
        latency=equipment_status_in.latency,
        department=department,
        last_update=datetime.now(),
        equipment_name="Главная касса",
    )

    id = orm.update_equipment_status(equipment_status)
    equipment_status.id = id

    last_incident = orm.find_last_unresolved_equipment_incident(equipment_status)

    if equipment_status.status in bad_statuses:
        if last_incident is None:
            await add_equipment_incident(equipment_status)
        await notify_workers_by_scope(
            FujiScope.bot_incident_monitoring,
            f"""Оборудование не доступно!
Предприятие: {equipment_status.department.name}
Тип оборудования: {equipment_status.equipment_name}""",
        )
    else:
        if last_incident is not None:
            last_incident.stage = IncidentStage.solved
            orm.update_equipment_incident_stage(last_incident)


async def add_equipment_incident(equipment_status: EquipmentStatusSchema):
    orm.add_equipment_incident(
        EquipmentIncidentSchema(
            equipment_status=equipment_status,
            incident_time=equipment_status.last_update,
            status=equipment_status.status,
            stage=IncidentStage.created,
        )
    )


def get_equipment_statuses() -> list[EquipmentStatusSchema]:
    return orm.get_equipment_statuses()


def get_incidents_history() -> list[EquipmentIncidentSchema]:
    return orm.get_resolved_equipment_incidents()


def get_pending_incidents() -> list[EquipmentIncidentSchema]:
    return orm.get_unresolved_equipment_incidents()


def get_incident_by_id(id: int) -> EquipmentIncidentSchema | None:
    return orm.get_equipment_incident_by_id(id)


def confirm_incident_by_id(id: int) -> None:
    incident = get_incident_by_id(id)
    incident.stage = IncidentStage.processed
    orm.update_equipment_incident_stage(incident)
