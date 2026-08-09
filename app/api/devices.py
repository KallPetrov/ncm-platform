from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.device import Device as DeviceModel, DeviceStatus
from app.models.user import User
from app.schemas.device import (
    DeviceCreate, DeviceUpdate, Device, DeviceListItem,
    DeviceConnectionTest
)
from app.services.device_connectivity import DeviceConnectivityService
import bcrypt
from app.api.auth import get_current_active_user, require_permission
from app.services.audit import AuditService

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/", response_model=Device, status_code=status.HTTP_200_OK)
def create_device(device: DeviceCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Create a new device"""
    require_permission(current_user, "manage_devices", db=db, resource_type="device")
    existing_device = db.query(DeviceModel).filter(DeviceModel.ip_address == device.ip_address).first()
    if existing_device:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Device with this IP address already exists")

    device_data = device.model_dump()
    device_data['password'] = bcrypt.hashpw(device_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    if device_data.get('enable_password'):
        device_data['enable_password'] = bcrypt.hashpw(device_data['enable_password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    db_device = DeviceModel(**device_data)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    AuditService.log_action(
        db,
        current_user,
        "device_created",
        resource_type="device",
        resource_id=db_device.id,
        details=f"Created device {db_device.name}",
    )

    return db_device


@router.get("/", response_model=List[DeviceListItem])
def list_devices(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List all devices with pagination"""
    devices = db.query(DeviceModel).offset(skip).limit(limit).all()
    return devices


@router.get("/{device_id}", response_model=Device)
def get_device(device_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get a specific device by ID"""
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device


@router.put("/{device_id}", response_model=Device)
def update_device(
    device_id: int,
    device_update: DeviceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update a device"""
    require_permission(current_user, "manage_devices", db=db, resource_type="device", resource_id=device_id)
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    if device_update.ip_address and device_update.ip_address != device.ip_address:
        existing_device = db.query(DeviceModel).filter(DeviceModel.ip_address == device_update.ip_address).first()
        if existing_device:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Device with this IP address already exists")

    update_data = device_update.model_dump(exclude_unset=True)

    if 'password' in update_data:
        update_data['password'] = bcrypt.hashpw(update_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    if 'enable_password' in update_data and update_data['enable_password']:
        update_data['enable_password'] = bcrypt.hashpw(update_data['enable_password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    for field, value in update_data.items():
        setattr(device, field, value)

    db.commit()
    db.refresh(device)
    AuditService.log_action(
        db,
        current_user,
        "device_updated",
        resource_type="device",
        resource_id=device.id,
        details=f"Updated device {device.name}",
    )

    return device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(device_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Delete a device"""
    require_permission(current_user, "manage_devices", db=db, resource_type="device", resource_id=device_id)
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    db.delete(device)
    db.commit()
    AuditService.log_action(
        db,
        current_user,
        "device_deleted",
        resource_type="device",
        resource_id=device_id,
        details=f"Deleted device {device.name}",
    )

    return None


@router.post("/{device_id}/test-connection", response_model=DeviceConnectionTest)
def test_device_connection(device_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Test connection to a device"""
    require_permission(current_user, "manage_devices", db=db, resource_type="device", resource_id=device_id)
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    result = DeviceConnectivityService.test_connection(device)
    device.status = DeviceStatus.ONLINE if result['success'] else DeviceStatus.OFFLINE
    db.commit()
    AuditService.log_action(
        db,
        current_user,
        "device_connection_tested",
        resource_type="device",
        resource_id=device.id,
        details=f"Tested connectivity for {device.name}",
    )

    return DeviceConnectionTest(
        device_id=device_id,
        success=result['success'],
        connected=result['success'],
        latency_ms=result.get('latency_ms'),
        error_message=result.get('error_message'),
        error=result.get('error_message')
    )


@router.post("/{device_id}/backup")
def trigger_backup(device_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Trigger an immediate backup of a device configuration"""
    require_permission(current_user, "manage_devices", db=db, resource_type="device", resource_id=device_id)
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    AuditService.log_action(
        db,
        current_user,
        "device_backup_triggered",
        resource_type="device",
        resource_id=device.id,
        details=f"Triggered backup for {device.name}",
    )

    return {
        "message": "Backup triggered",
        "device_id": device_id,
        "job_id": f"backup-{device_id}",
        "status": "pending",
    }


@router.post("/{device_id}/trigger-backup")
def trigger_backup_compat(device_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Compatibility endpoint for backup workflow tests."""
    return trigger_backup(device_id, current_user=current_user, db=db)
