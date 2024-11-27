from fastapi.routing import APIRouter

import app.services.equipment_status as equipment_service
from app.infra.database.schemas import EquipmentStatusSchemaIn

router = APIRouter()


@router.patch("/{asterisk_id}")
async def update_equipment_status(
    asterisk_id: str, equipment_status: EquipmentStatusSchemaIn
):
    await equipment_service.update_equipment_status(asterisk_id, equipment_status)
