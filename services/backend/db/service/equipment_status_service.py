from datetime import datetime

from settings import logger

from db.schemas import EquipmentStatusSchemaIn, EquipmentStatusSchema
from db.models import Department
from db import orm

bad_statuses = ["Не доступна"]


def update_equipment_status(
    asterisk_id: str, equipment_status_in: EquipmentStatusSchemaIn
) -> bool:
    """Updates equipment status, adds incident if `equipment_status_in.status` is bad.

    If status not exist in db creates it.s
    """
    if (
        department := orm.find_department_by_column(Department.asterisk_id, asterisk_id)
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
        equipment_name="Предприятие",
    )

    orm.update_equipment_status(equipment_status)

    if equipment_status.status in bad_statuses:
        add_equipment_incident(equipment_status)


def add_equipment_incident(equipment_status: EquipmentStatusSchema):
    orm.add_equipment_incident(equipment_status)
