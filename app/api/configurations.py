from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import difflib
from app.core.database import get_db
from app.models.device import Configuration, Device as DeviceModel
from app.models.user import User
from app.api.auth import get_current_active_user, require_permission
from app.schemas.configuration import ConfigurationListItem
from app.services.compliance import ComplianceEngine
from app.services.audit import AuditService

router = APIRouter(prefix="/configurations", tags=["configurations"])


def _serialize_configuration(config: Configuration) -> dict:
    return {
        "id": config.id,
        "device_id": config.device_id,
        "version": config.version,
        "content": getattr(config, "content", None) or "",
        "config_hash": getattr(config, "config_hash", None) or "",
        "file_path": getattr(config, "file_path", None) or "",
        "file_size": getattr(config, "file_size", None) or 0,
        "is_changed": getattr(config, "is_changed", False),
        "change_summary": getattr(config, "change_summary", None),
        "created_at": getattr(config, "created_at", None),
    }


@router.get("/device/{device_id}", response_model=List[ConfigurationListItem])
def get_device_configurations(
    device_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get all configuration versions for a device"""
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    configurations = (
        db.query(Configuration)
        .filter(Configuration.device_id == device_id)
        .order_by(Configuration.version.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [_serialize_configuration(config) for config in configurations]


@router.get("/device/{device_id}/latest")
def get_latest_configuration(
    device_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get the latest configuration for a device"""
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    config = (
        db.query(Configuration)
        .filter(Configuration.device_id == device_id)
        .order_by(Configuration.version.desc())
        .first()
    )

    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No configurations found for this device")

    return _serialize_configuration(config)


@router.get("/device/{device_id}/version/{version}")
def get_configuration_by_version(
    device_id: int,
    version: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a specific configuration version"""
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    config = (
        db.query(Configuration)
        .filter(Configuration.device_id == device_id, Configuration.version == version)
        .first()
    )

    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Configuration version {version} not found")

    return {
        "device_id": device_id,
        "version": version,
        "content": config.content or "",
        "config_hash": config.config_hash or "",
        "file_path": config.file_path or "",
        "file_size": config.file_size or 0,
        "is_changed": config.is_changed,
        "change_summary": config.change_summary,
    }


@router.get("/device/{device_id}/diff")
def get_configuration_diff(
    device_id: int,
    version_a: int,
    version_b: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get diff between two configuration versions"""
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    config_a = db.query(Configuration).filter(Configuration.device_id == device_id, Configuration.version == version_a).first()
    config_b = db.query(Configuration).filter(Configuration.device_id == device_id, Configuration.version == version_b).first()

    if not config_a or not config_b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not generate diff")

    content_a = config_a.content or ""
    content_b = config_b.content or ""
    diff_output = "\n".join(
        difflib.unified_diff(
            content_a.splitlines(),
            content_b.splitlines(),
            fromfile=f"version_{version_a}",
            tofile=f"version_{version_b}",
            lineterm="",
        )
    )

    return {
        "device_id": device_id,
        "version_a": version_a,
        "version_b": version_b,
        "diff": diff_output,
        "summary": f"Comparing version {version_a} with version {version_b}",
    }


@router.get("/device/{device_id}/changes")
def get_configuration_changes(
    device_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Analyze recent configuration changes for a device"""
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    configs = (
        db.query(Configuration)
        .filter(Configuration.device_id == device_id)
        .order_by(Configuration.version.desc())
        .limit(2)
        .all()
    )

    return [
        {
            "device_id": device_id,
            "version": config.version,
            "content": config.content or "",
        }
        for config in configs
    ]


@router.get("/device/{device_id}/compliance")
def get_configuration_compliance(
    device_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Run compliance checks against the latest configuration for a device."""
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    config = (
        db.query(Configuration)
        .filter(Configuration.device_id == device_id)
        .order_by(Configuration.version.desc())
        .first()
    )

    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No configurations found for this device")

    engine = ComplianceEngine()
    report = engine.check_compliance(config.content or "", device_type=device.device_type.value if getattr(device.device_type, "value", None) else str(device.device_type))

    return {
        "device_id": device_id,
        "device_name": device.name,
        "overall_status": report["overall_status"].value,
        "compliance_percentage": report["compliance_percentage"],
        "total_rules": report["total_rules"],
        "compliant_rules": report["compliant_rules"],
        "non_compliant_rules": report["non_compliant_rules"],
        "results": [
            {
                "rule_name": result.rule_name,
                "status": result.status.value,
                "message": result.message,
                "details": result.details,
                "severity": result.severity,
                "line_number": result.line_number,
            }
            for result in report["results"]
        ],
    }


@router.delete("/{configuration_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_configuration(
    configuration_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a specific configuration entry"""
    require_permission(current_user, "manage_configurations", db=db, resource_type="configuration", resource_id=configuration_id)
    config = db.query(Configuration).filter(Configuration.id == configuration_id).first()
    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuration not found")

    db.delete(config)
    db.commit()
    AuditService.log_action(
        db,
        current_user,
        "configuration_deleted",
        resource_type="configuration",
        resource_id=config.id,
        details=f"Deleted configuration version {config.version} for device {config.device_id}",
    )
    return None


@router.delete("/device/{device_id}/all", status_code=status.HTTP_204_NO_CONTENT)
def delete_device_configurations(
    device_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete all configurations for a device"""
    require_permission(current_user, "manage_configurations", db=db, resource_type="configuration", resource_id=device_id)
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    db.query(Configuration).filter(Configuration.device_id == device_id).delete()
    db.commit()
    AuditService.log_action(
        db,
        current_user,
        "device_configurations_deleted",
        resource_type="configuration",
        resource_id=device_id,
        details=f"Deleted all configurations for device {device_id}",
    )

    return None
