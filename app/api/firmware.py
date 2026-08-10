from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.models.firmware import FirmwareImage, UpgradeJob
from app.models.device import Device
from app.api.auth import get_current_active_user, require_permission
from app.schemas.firmware import FirmwareImageCreate, FirmwareImageResponse, UpgradeJobCreate, UpgradeJobResponse
from app.services.firmware_upgrade import FirmwareUpgradeService
from app.services.audit import AuditService

router = APIRouter(prefix="/firmware", tags=["firmware"])


@router.post("/images", response_model=FirmwareImageResponse, status_code=status.HTTP_201_CREATED)
def register_firmware_image(
    payload: FirmwareImageCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Register/upload a firmware image in the platform database."""
    require_permission(current_user, "manage_devices", db=db, resource_type="firmware")

    firmware = FirmwareImage(
        filename=payload.filename,
        version=payload.version,
        device_type=payload.device_type,
        vendor=payload.vendor,
        md5_hash=payload.md5_hash,
        file_size=payload.file_size,
        file_path=payload.file_path
    )
    db.add(firmware)
    db.commit()
    db.refresh(firmware)

    AuditService.log_action(
        db,
        current_user,
        "firmware_registered",
        resource_type="firmware",
        resource_id=firmware.id,
        details=f"Registered firmware version {firmware.version} for vendor {firmware.vendor}"
    )

    return firmware


@router.get("/images", response_model=List[FirmwareImageResponse])
def list_firmware_images(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Retrieve all registered firmware images."""
    return db.query(FirmwareImage).all()


@router.post("/upgrade", response_model=UpgradeJobResponse, status_code=status.HTTP_201_CREATED)
def trigger_firmware_upgrade(
    payload: UpgradeJobCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Trigger an automated firmware upgrade workflow on a device."""
    require_permission(current_user, "manage_devices", db=db, resource_type="firmware")

    # Verify device and firmware exist
    device = db.query(Device).filter(Device.id == payload.device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    firmware = db.query(FirmwareImage).filter(FirmwareImage.id == payload.firmware_image_id).first()
    if not firmware:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Firmware image not found")

    # Create job in database
    job = UpgradeJob(
        device_id=payload.device_id,
        firmware_image_id=payload.firmware_image_id,
        status="pending"
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    AuditService.log_action(
        db,
        current_user,
        "firmware_upgrade_started",
        resource_type="upgrade_job",
        resource_id=job.id,
        details=f"Started firmware upgrade to version {firmware.version} on device {device.name}"
    )

    # Perform the upgrade synchronously in this API handler for validation
    # (In high-scale enterprise configurations, this can be offloaded to Celery background task)
    FirmwareUpgradeService.perform_upgrade(db, job.id)
    db.refresh(job)

    return job


@router.get("/jobs/{job_id}", response_model=UpgradeJobResponse)
def get_upgrade_job_status(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Retrieve the status and results of a firmware upgrade job."""
    job = db.query(UpgradeJob).filter(UpgradeJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upgrade job not found")
    return job
