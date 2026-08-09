from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.device import Device, Configuration
from app.models.user import User
from app.api.auth import get_current_active_user
from app.services.change_detection import ChangeDetectionService

router = APIRouter(prefix="/change-management", tags=["change-management"])


@router.get("/device/{device_id}/analysis")
def analyze_device_changes(
    device_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    service = ChangeDetectionService()
    result = service.analyze_configuration_changes(device_id, device.name, db)

    has_changes = result.get("has_changes", result.get("has_changed", False))
    if not has_changes and result.get("message"):
        return {
            "device_id": device_id,
            "device_name": device.name,
            "has_changes": False,
            "message": result["message"],
        }

    return {
        "device_id": device_id,
        "device_name": device.name,
        **result,
    }
