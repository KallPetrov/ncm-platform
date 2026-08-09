from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.device import Device
from app.models.user import User
from app.api.auth import get_current_active_user
from app.services.automation import AutomationService

router = APIRouter(prefix="/automation", tags=["automation"])


@router.get("/templates")
def list_predefined_templates(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = AutomationService()
    templates = service.get_predefined_templates()
    return [
        {"name": name, "content": content}
        for name, content in templates.items()
    ]


@router.post("/validate-template")
def validate_template(payload: dict, current_user: User = Depends(get_current_active_user)):
    service = AutomationService()
    template = payload.get("template", "")
    return service.validate_template(template)


@router.post("/apply")
def apply_template(
    payload: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = AutomationService()
    device_ids = payload.get("device_ids", [])
    template = payload.get("template", "")
    variables = payload.get("variables", {})

    devices = db.query(Device).filter(Device.id.in_(device_ids)).all()
    if not devices:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No devices found")

    results = service.apply_template_to_devices(devices, template, variables, save_config=False)
    return {
        "success": True,
        "total_devices": len(devices),
        "results": results,
    }
