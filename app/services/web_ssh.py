import secrets
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.device import Device
from app.models.web_ssh import SSHSession, KeystrokeLog
from app.services.device_connectivity import DeviceConnectivityService


class WebSSHService:
    """
    Web SSH & Session Recording Service (Module 3.4)

    Provides secure PAM proxy authentication, interactive terminal connection
    handling, and real-time keystroke/command logging for compliance audits.
    """

    @classmethod
    def create_session(cls, db: Session, user_id: int, device_id: int) -> SSHSession:
        """
        Creates and allocates a secure SSHSession with a cryptographically
        secure session token.
        """
        token = f"ssh_tok_{secrets.token_urlsafe(32)}"
        session = SSHSession(
            user_id=user_id,
            device_id=device_id,
            session_token=token,
            status="active"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @classmethod
    def execute_and_record_command(
        cls, db: Session, session_token: str, command: str, is_testing: bool = False
    ) -> Dict[str, Any]:
        """
        Securely executes a command on behalf of the user (Network PAM proxy)
        and records the command (Keystroke recording) and output sample.
        """
        session = db.query(SSHSession).filter(
            SSHSession.session_token == session_token,
            SSHSession.status == "active"
        ).first()

        if not session:
            return {"success": False, "error": "Active SSH session not found"}

        device = session.device

        # 1. Execute the command securely
        if is_testing:
            # Simulated output
            output = f"Output of '{command}' on {device.name} (Simulated)"
            success = True
            error_msg = None
        else:
            # Real Netmiko execution via connection pooling
            res = DeviceConnectivityService.send_command(device, command)
            output = res.get("output") or ""
            success = res["success"]
            error_msg = res.get("error_message")

        if not success:
            return {"success": False, "error": error_msg or "Failed to execute command"}

        # 2. Record keystroke/command (Keystroke Logging)
        keystroke_entry = KeystrokeLog(
            ssh_session_id=session.id,
            typed_command=command,
            output_sample=output[:1000] if output else ""
        )
        db.add(keystroke_entry)
        db.commit()

        return {
            "success": True,
            "command": command,
            "output": output,
            "timestamp": datetime.now().isoformat()
        }

    @classmethod
    def close_session(cls, db: Session, session_token: str) -> Optional[SSHSession]:
        """
        Closes an active SSHSession.
        """
        session = db.query(SSHSession).filter(
            SSHSession.session_token == session_token,
            SSHSession.status == "active"
        ).first()

        if session:
            session.status = "closed"
            session.closed_at = datetime.now()
            db.commit()
            db.refresh(session)
            return session
        return None
