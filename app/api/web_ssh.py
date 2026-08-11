from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.models.web_ssh import SSHSession, KeystrokeLog
from app.models.device import Device
from app.api.auth import get_current_active_user, require_permission
from app.schemas.web_ssh import SSHSessionCreate, SSHSessionResponse, KeystrokeLogResponse
from app.services.web_ssh import WebSSHService
from app.services.audit import AuditService

router = APIRouter(prefix="/ssh", tags=["ssh"])


@router.post("/sessions", response_model=SSHSessionResponse, status_code=status.HTTP_201_CREATED)
def open_ssh_session(
    payload: SSHSessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Initiates a secure Web-SSH session to a network device (Network PAM proxy).
    """
    device = db.query(Device).filter(Device.id == payload.device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")

    session = WebSSHService.create_session(db, current_user.id, payload.device_id)

    AuditService.log_action(
        db,
        current_user,
        "ssh_session_opened",
        resource_type="ssh_session",
        resource_id=session.id,
        details=f"Opened secure SSH terminal session to device {device.name}"
    )

    return session


@router.post("/execute")
def execute_terminal_command(
    payload: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Executes a command within an active SSH session and logs the keystrokes.
    """
    token = payload.get("session_token")
    command = payload.get("command")

    if not token or not command:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="session_token and command are required")

    import os
    is_testing = os.getenv("TESTING") == "1"

    result = WebSSHService.execute_and_record_command(db, token, command, is_testing=is_testing)
    if not result["success"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result["error"])

    return result


@router.post("/close")
def close_ssh_session(
    payload: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Closes an active Web-SSH terminal session.
    """
    token = payload.get("session_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="session_token is required")

    session = WebSSHService.close_session(db, token)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active SSH session not found")

    AuditService.log_action(
        db,
        current_user,
        "ssh_session_closed",
        resource_type="ssh_session",
        resource_id=session.id,
        details=f"Closed SSH terminal session to device {session.device_id}"
    )

    return {"success": True, "message": "Session closed successfully"}


@router.get("/sessions/{session_id}/logs", response_model=List[KeystrokeLogResponse])
def get_session_keystroke_logs(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves keystroke/command records for audit and compliance. Limited to admins/auditors.
    """
    require_permission(current_user, "view_audit_logs", db=db, resource_type="ssh_session", resource_id=session_id)

    logs = db.query(KeystrokeLog).filter(KeystrokeLog.ssh_session_id == session_id).all()
    return logs
