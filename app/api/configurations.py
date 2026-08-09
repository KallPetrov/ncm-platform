from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.device import Configuration, Device as DeviceModel
from app.schemas.configuration import (
    ConfigurationListItem, ConfigurationDiff
)
from app.services.backup_engine import BackupEngine
from app.services.change_detection import ChangeDetectionService
from app.services.git_storage import GitStorageService

router = APIRouter(prefix="/configurations", tags=["configurations"])


@router.get("/device/{device_id}", response_model=List[ConfigurationListItem])
def get_device_configurations(
    device_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get all configuration versions for a device"""
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    configurations = db.query(Configuration).filter(
        Configuration.device_id == device_id
    ).order_by(Configuration.version.desc()).offset(skip).limit(limit).all()
    
    return configurations


@router.get("/device/{device_id}/latest")
def get_latest_configuration(device_id: int, db: Session = Depends(get_db)):
    """Get the latest configuration for a device"""
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    git_storage = GitStorageService()
    latest_config = git_storage.get_latest_configuration(device_id, device.name)
    
    if not latest_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No configurations found for this device"
        )
    
    return latest_config


@router.get("/device/{device_id}/version/{version}")
def get_configuration_by_version(
    device_id: int,
    version: int,
    db: Session = Depends(get_db)
):
    """Get a specific configuration version"""
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    git_storage = GitStorageService()
    config = git_storage.get_configuration(device_id, device.name, version)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration version {version} not found"
        )
    
    return {
        "device_id": device_id,
        "version": version,
        "configuration": config
    }


@router.get("/device/{device_id}/diff")
def get_configuration_diff(
    device_id: int,
    version_a: int,
    version_b: int,
    db: Session = Depends(get_db)
):
    """Get diff between two configuration versions"""
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    backup_engine = BackupEngine()
    diff = backup_engine.get_configuration_diff(device_id, version_a, version_b, db)
    
    if not diff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not generate diff"
        )
    
    return diff


@router.get("/device/{device_id}/changes")
def get_configuration_changes(device_id: int, db: Session = Depends(get_db)):
    """Analyze recent configuration changes for a device"""
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    change_detection = ChangeDetectionService()
    changes = change_detection.analyze_configuration_changes(device_id, device.name, db)
    
    return changes


@router.delete("/device/{device_id}/all", status_code=status.HTTP_204_NO_CONTENT)
def delete_device_configurations(device_id: int, db: Session = Depends(get_db)):
    """Delete all configurations for a device"""
    device = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    git_storage = GitStorageService()
    success = git_storage.delete_device_configurations(device_id, device.name)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete configurations"
        )
    
    # Delete from database
    db.query(Configuration).filter(Configuration.device_id == device_id).delete()
    db.commit()
    
    return None
