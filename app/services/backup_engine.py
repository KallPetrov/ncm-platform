from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime
from app.models.device import Device, Configuration, BackupJob, DeviceStatus
from app.services.device_connectivity import DeviceConnectivityService
from app.services.git_storage import GitStorageService
from app.core.security import decrypt_password


class BackupEngine:
    """Engine for managing configuration backups"""
    
    def __init__(self):
        self.git_storage = GitStorageService()
    
    def perform_backup(self, device: Device, db: Session) -> Dict[str, Any]:
        """Perform a configuration backup for a device"""
        # Create backup job record
        backup_job = BackupJob(device_id=device.id, status="running")
        db.add(backup_job)
        db.commit()
        db.refresh(backup_job)
        
        try:
            # Decrypt password (in real implementation, use proper decryption)
            # For now, we'll use the stored password directly
            # device.password = decrypt_password(device.password)
            # if device.enable_password:
            #     device.enable_password = decrypt_password(device.enable_password)
            
            # Get configuration from device
            result = DeviceConnectivityService.get_configuration(device)
            
            if not result['success']:
                backup_job.status = "failed"
                backup_job.error_message = result['error_message']
                backup_job.completed_at = datetime.now()
                db.commit()
                
                return {
                    'success': False,
                    'backup_job_id': backup_job.id,
                    'error_message': result['error_message']
                }
            
            configuration = result['configuration']
            
            # Get latest configuration version for this device
            latest_config = db.query(Configuration).filter(
                Configuration.device_id == device.id
            ).order_by(Configuration.version.desc()).first()
            
            next_version = 1 if latest_config is None else latest_config.version + 1
            
            # Store configuration in Git
            git_result = self.git_storage.store_configuration(
                device_id=device.id,
                device_name=device.name,
                configuration=configuration,
                version=next_version,
                commit_message=f"Backup for device {device.name} (ID: {device.id})"
            )
            
            if not git_result['success']:
                backup_job.status = "failed"
                backup_job.error_message = f"Git storage failed: {git_result['error_message']}"
                backup_job.completed_at = datetime.now()
                db.commit()
                
                return {
                    'success': False,
                    'backup_job_id': backup_job.id,
                    'error_message': git_result['error_message']
                }
            
            # Check for changes
            is_changed = False
            change_summary = None
            
            if latest_config:
                if latest_config.config_hash != git_result['config_hash']:
                    is_changed = True
                    change_summary = self._generate_change_summary(
                        latest_config.config_hash,
                        git_result['config_hash']
                    )
            
            # Create configuration record
            configuration_record = Configuration(
                device_id=device.id,
                version=next_version,
                config_hash=git_result['config_hash'],
                file_path=git_result['file_path'],
                file_size=len(configuration.encode('utf-8')),
                is_changed=is_changed,
                change_summary=change_summary
            )
            db.add(configuration_record)
            
            # Update device status and last backup time
            device.status = DeviceStatus.ONLINE
            device.last_backup = datetime.now()
            device.last_seen = datetime.now()
            
            # Update backup job
            backup_job.status = "success"
            backup_job.completed_at = datetime.now()
            
            db.commit()
            
            return {
                'success': True,
                'backup_job_id': backup_job.id,
                'configuration_id': configuration_record.id,
                'version': next_version,
                'is_changed': is_changed,
                'change_summary': change_summary
            }
            
        except Exception as e:
            backup_job.status = "failed"
            backup_job.error_message = str(e)
            backup_job.completed_at = datetime.now()
            db.commit()
            
            return {
                'success': False,
                'backup_job_id': backup_job.id,
                'error_message': str(e)
            }
    
    def _generate_change_summary(self, old_hash: str, new_hash: str) -> str:
        """Generate a summary of configuration changes"""
        return f"Configuration changed from {old_hash[:8]} to {new_hash[:8]}"
    
    def get_device_configurations(self, device_id: int, db: Session) -> list:
        """Get all configuration versions for a device"""
        configurations = db.query(Configuration).filter(
            Configuration.device_id == device_id
        ).order_by(Configuration.version.desc()).all()
        
        return configurations
    
    def get_configuration_diff(
        self, 
        device_id: int, 
        version_a: int, 
        version_b: int, 
        db: Session
    ) -> Optional[Dict[str, Any]]:
        """Get diff between two configuration versions"""
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            return None
        
        config_a = db.query(Configuration).filter(
            Configuration.device_id == device_id,
            Configuration.version == version_a
        ).first()
        
        config_b = db.query(Configuration).filter(
            Configuration.device_id == device_id,
            Configuration.version == version_b
        ).first()
        
        if not config_a or not config_b:
            return None
        
        # Get diff from Git storage
        diff = self.git_storage.compare_configurations(
            device_id=device_id,
            device_name=device.name,
            version_a=version_a,
            version_b=version_b
        )
        
        return {
            'device_id': device_id,
            'version_a': version_a,
            'version_b': version_b,
            'diff_output': diff,
            'summary': f"Comparing version {version_a} with version {version_b}"
        }
    
    def get_backup_job_status(self, job_id: int, db: Session) -> Optional[Dict[str, Any]]:
        """Get status of a backup job"""
        job = db.query(BackupJob).filter(BackupJob.id == job_id).first()
        if not job:
            return None
        
        return {
            'id': job.id,
            'device_id': job.device_id,
            'status': job.status,
            'error_message': job.error_message,
            'started_at': job.started_at,
            'completed_at': job.completed_at
        }
    
    def get_device_backup_history(self, device_id: int, db: Session, limit: int = 50) -> list:
        """Get backup job history for a device"""
        jobs = db.query(BackupJob).filter(
            BackupJob.device_id == device_id
        ).order_by(BackupJob.started_at.desc()).limit(limit).all()
        
        return jobs
