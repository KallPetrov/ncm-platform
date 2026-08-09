from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.device import Device as DeviceModel
from app.models.user import User
from app.schemas.device import (
    DeviceCreate, DeviceUpdate, Device, DeviceListItem,
    DeviceConnectionTest, DeviceStatus
)
from app.services.device_connectivity import DeviceConnectivityService
import bcrypt
from app.api.auth import get_current_active_user

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/", response_model=Device, status_code=status.HTTP_201_CREATED)
def create_device(device: DeviceCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Create a new device"""
    # Check if IP address already exists
    existing_device = db.query(DeviceModel).filter(DeviceModel.ip_address == device.ip_address).first()
    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device with this IP address already exists"
        )
    
    # Encrypt password
    device_data = device.dict()
    device_data['password'] = bcrypt.hashpw(device_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    if device_data.get('enable_password'):
        device_data['enable_password'] = bcrypt.hashpw(device_data['enable_password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    db_device = DeviceModel(**device_data)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    
    return db_device


@router.get("/", response_model=List[DeviceListItem])
def list_devices(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all devices with pagination"""
    devices = db.query(DeviceModel).offset(skip).limit(limit).all()
    return devices


@router.get("/{device_id}", response_model=Device)
def get_device(device_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get a specific device by ID"""
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    return device


@router.put("/{device_id}", response_model=Device)
def update_device(
    device_id: int,
    device_update: DeviceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a device"""
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    # Check if IP address is being changed and if it's already taken
    if device_update.ip_address and device_update.ip_address != device.ip_address:
        existing_device = db.query(DeviceModel).filter(
            DeviceModel.ip_address == device_update.ip_address
        ).first()
        if existing_device:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Device with this IP address already exists"
            )

    # Update fields
    update_data = device_update.dict(exclude_unset=True)

    # Encrypt passwords if provided
    if 'password' in update_data:
        update_data['password'] = bcrypt.hashpw(update_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    if 'enable_password' in update_data and update_data['enable_password']:
        update_data['enable_password'] = bcrypt.hashpw(update_data['enable_password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    for field, value in update_data.items():
        setattr(device, field, value)

    db.commit()
    db.refresh(device)

    return device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(device_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Delete a device"""
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    db.delete(device)
    db.commit()

    return None


@router.post("/{device_id}/test-connection", response_model=DeviceConnectionTest)
def test_device_connection(device_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Test connection to a device"""
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    # Decrypt password (in real implementation, use proper decryption)
    # For now, we'll use the stored password directly
    result = DeviceConnectivityService.test_connection(device)

    # Update device status based on test result
    device.status = DeviceStatus.ONLINE if result['success'] else DeviceStatus.OFFLINE
    db.commit()

    return DeviceConnectionTest(
        device_id=device_id,
        success=result['success'],
        latency_ms=result.get('latency_ms'),
        error_message=result.get('error_message')
    )


@router.post("/{device_id}/backup")
def trigger_backup(device_id: int, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Trigger an immediate backup of a device configuration"""
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    # This will be implemented with Celery tasks
    # For now, return a placeholder response
    return {
        "message": "Backup triggered",
        "device_id": device_id,
        "status": "pending"
    }
