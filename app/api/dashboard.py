from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.device import BackupJob, Configuration, Device
from app.models.user import User
from app.api.auth import get_current_active_user
from app.services.compliance import ComplianceEngine

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview")
def get_dashboard_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Return a simple operational overview for the dashboard UI."""
    total_devices = db.query(Device).count()
    online_devices = db.query(Device).filter(Device.status == "online").count()
    offline_devices = db.query(Device).filter(Device.status == "offline").count()

    total_configurations = db.query(Configuration).count()
    successful_backup_jobs = db.query(BackupJob).filter(BackupJob.status == "success").count()
    pending_backup_jobs = db.query(BackupJob).filter(BackupJob.status == "pending").count()

    latest_config = (
        db.query(Configuration)
        .order_by(Configuration.version.desc())
        .first()
    )

    compliance_engine = ComplianceEngine()
    compliance_report = compliance_engine.check_compliance(latest_config.content if latest_config else "")

    return {
        "total_devices": total_devices,
        "online_devices": online_devices,
        "offline_devices": offline_devices,
        "total_configurations": total_configurations,
        "successful_backup_jobs": successful_backup_jobs,
        "pending_backup_jobs": pending_backup_jobs,
        "latest_configuration_version": latest_config.version if latest_config else None,
        "compliance_summary": {
            "overall_status": compliance_report["overall_status"].value,
            "compliance_percentage": compliance_report["compliance_percentage"],
            "total_rules": compliance_report["total_rules"],
            "compliant_rules": compliance_report["compliant_rules"],
            "non_compliant_rules": compliance_report["non_compliant_rules"],
        },
    }
