from celery import shared_task
from sqlalchemy.orm import Session
from datetime import datetime
from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.backup_engine import BackupEngine
from app.models.device import Device
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, name="app.tasks.backup_tasks.perform_device_backup")
def perform_device_backup(self, device_id: int):
    """Perform a backup for a specific device"""
    db = SessionLocal()
    try:
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            logger.error(f"Device {device_id} not found")
            return {'success': False, 'error': 'Device not found'}
        
        backup_engine = BackupEngine()
        result = backup_engine.perform_backup(device, db)
        
        logger.info(f"Backup completed for device {device_id}: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Backup failed for device {device_id}: {str(e)}")
        return {'success': False, 'error': str(e)}
    finally:
        db.close()


@shared_task(bind=True, name="app.tasks.backup_tasks.perform_scheduled_backups")
def perform_scheduled_backups(self):
    """Perform backups for all devices with auto-backup enabled"""
    db = SessionLocal()
    try:
        # Get all devices with auto-backup enabled
        devices = db.query(Device).filter(
            Device.auto_backup_enabled == True
        ).all()
        
        logger.info(f"Starting scheduled backups for {len(devices)} devices")
        
        results = []
        for device in devices:
            try:
                # Trigger backup task for each device
                task = perform_device_backup.delay(device.id)
                results.append({
                    'device_id': device.id,
                    'device_name': device.name,
                    'task_id': task.id,
                    'status': 'queued'
                })
            except Exception as e:
                logger.error(f"Failed to queue backup for device {device.id}: {str(e)}")
                results.append({
                    'device_id': device.id,
                    'device_name': device.name,
                    'status': 'failed',
                    'error': str(e)
                })
        
        logger.info(f"Scheduled backups queued: {len(results)} devices")
        return {
            'total_devices': len(devices),
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Scheduled backups failed: {str(e)}")
        return {'success': False, 'error': str(e)}
    finally:
        db.close()


@shared_task(bind=True, name="app.tasks.backup_tasks.backup_single_device")
def backup_single_device(self, device_id: int):
    """Backup a single device (triggered by user request)"""
    db = SessionLocal()
    try:
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            logger.error(f"Device {device_id} not found")
            return {'success': False, 'error': 'Device not found'}
        
        backup_engine = BackupEngine()
        result = backup_engine.perform_backup(device, db)
        
        logger.info(f"Manual backup completed for device {device_id}: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Manual backup failed for device {device_id}: {str(e)}")
        return {'success': False, 'error': str(e)}
    finally:
        db.close()


@shared_task(bind=True, name="app.tasks.backup_tasks.check_device_status")
def check_device_status(self, device_id: int):
    """Check the status of a device and update it"""
    db = SessionLocal()
    try:
        from app.services.device_connectivity import DeviceConnectivityService
        from app.models.device import DeviceStatus
        
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            logger.error(f"Device {device_id} not found")
            return {'success': False, 'error': 'Device not found'}
        
        # Test connection
        result = DeviceConnectivityService.test_connection(device)
        
        # Update device status
        device.status = DeviceStatus.ONLINE if result['success'] else DeviceStatus.OFFLINE
        if result['success']:
            device.last_seen = datetime.now()
        
        db.commit()
        
        logger.info(f"Status check completed for device {device_id}: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Status check failed for device {device_id}: {str(e)}")
        return {'success': False, 'error': str(e)}
    finally:
        db.close()


@shared_task(bind=True, name="app.tasks.backup_tasks.check_all_devices_status")
def check_all_devices_status(self):
    """Check status of all devices"""
    db = SessionLocal()
    try:
        devices = db.query(Device).all()
        
        logger.info(f"Starting status check for {len(devices)} devices")
        
        results = []
        for device in devices:
            try:
                task = check_device_status.delay(device.id)
                results.append({
                    'device_id': device.id,
                    'device_name': device.name,
                    'task_id': task.id,
                    'status': 'queued'
                })
            except Exception as e:
                logger.error(f"Failed to queue status check for device {device.id}: {str(e)}")
                results.append({
                    'device_id': device.id,
                    'device_name': device.name,
                    'status': 'failed',
                    'error': str(e)
                })
        
        logger.info(f"Status checks queued: {len(results)} devices")
        return {
            'total_devices': len(devices),
            'results': results
        }
        
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        return {'success': False, 'error': str(e)}
    finally:
        db.close()
