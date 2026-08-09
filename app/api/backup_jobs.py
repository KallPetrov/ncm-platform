from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.device import BackupJob, Device
from app.schemas.backup_job import BackupJobListItem, BackupJobSummary
from app.services.backup_engine import BackupEngine
from app.tasks.backup_tasks import backup_single_device

router = APIRouter(prefix="/backup-jobs", tags=["backup-jobs"])


@router.get("/", response_model=List[BackupJobListItem])
def list_backup_jobs(
    skip: int = 0,
    limit: int = 100,
    device_id: int = None,
    db: Session = Depends(get_db)
):
    """List backup jobs with optional filtering by device"""
    query = db.query(BackupJob)
    
    if device_id:
        query = query.filter(BackupJob.device_id == device_id)
    
    jobs = query.order_by(BackupJob.started_at.desc()).offset(skip).limit(limit).all()

    # Populate device names and error messages dynamically
    jobs_list = []
    for job in jobs:
        device_name = job.device.name if job.device else "Unknown Device"
        jobs_list.append({
            "id": job.id,
            "device_id": job.device_id,
            "device_name": device_name,
            "status": job.status,
            "error_message": job.error_message,
            "started_at": job.started_at,
            "completed_at": job.completed_at
        })
    return jobs_list


@router.get("/{job_id}")
def get_backup_job(job_id: int, db: Session = Depends(get_db)):
    """Get a specific backup job by ID"""
    job = db.query(BackupJob).filter(BackupJob.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backup job not found"
        )
    return job


@router.get("/device/{device_id}", response_model=List[BackupJobListItem])
def get_device_backup_jobs(
    device_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get backup job history for a specific device"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    backup_engine = BackupEngine()
    jobs = backup_engine.get_device_backup_history(device_id, db, limit)
    
    return jobs


@router.get("/summary/overview")
def get_backup_summary(db: Session = Depends(get_db)):
    """Get summary of backup jobs"""
    total = db.query(BackupJob).count()
    pending = db.query(BackupJob).filter(BackupJob.status == "pending").count()
    running = db.query(BackupJob).filter(BackupJob.status == "running").count()
    success = db.query(BackupJob).filter(BackupJob.status == "success").count()
    failed = db.query(BackupJob).filter(BackupJob.status == "failed").count()
    
    return BackupJobSummary(
        total_jobs=total,
        pending=pending,
        running=running,
        success=success,
        failed=failed
    )


@router.post("/device/{device_id}/trigger")
def trigger_device_backup(device_id: int, db: Session = Depends(get_db)):
    """Trigger an immediate backup for a device"""
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Trigger async backup task
    task = backup_single_device.delay(device_id)
    
    return {
        "message": "Backup triggered",
        "device_id": device_id,
        "task_id": task.id,
        "status": "pending"
    }


@router.post("/trigger-all")
def trigger_all_backups(db: Session = Depends(get_db)):
    """Trigger backups for all devices with auto-backup enabled"""
    from app.tasks.backup_tasks import perform_scheduled_backups
    
    task = perform_scheduled_backups.delay()
    
    return {
        "message": "Scheduled backups triggered for all devices",
        "task_id": task.id,
        "status": "pending"
    }
