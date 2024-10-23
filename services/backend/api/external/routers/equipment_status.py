from fastapi.routing import APIRouter

from db.service import equipment_status_service
from db.schemas import EquipmentStatusSchemaIn

router = APIRouter()


@router.patch("/{asterisk_id}")
async def update_equipment_status(
    asterisk_id: str, equipment_status: EquipmentStatusSchemaIn
):
    equipment_status_service.update_equipment_status(asterisk_id, equipment_status)
