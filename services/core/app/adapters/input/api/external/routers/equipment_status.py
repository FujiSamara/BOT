from fastapi.routing import APIRouter

from app.services import equipment_status_service
from app.infra.database.schemas import EquipmentStatusSchemaIn

router = APIRouter()


@router.patch("/{asterisk_id}")
async def update_equipment_status(
    asterisk_id: str, equipment_status: EquipmentStatusSchemaIn
):
    await equipment_status_service.update_equipment_status(
        asterisk_id, equipment_status
    )
