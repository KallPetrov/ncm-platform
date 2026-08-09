from typing import Optional
from sqlalchemy.orm import Session
from app.models.audit import AuditLog
from app.models.user import User


class AuditService:
    @staticmethod
    def log_action(
        db: Session,
        user: Optional[User],
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
        role: Optional[str] = None,
    ) -> AuditLog:
        entry = AuditLog(
            user_id=user.id if user else None,
            username=user.username if user else None,
            role=role or ("admin" if user and user.is_admin else "user" if user else None),
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    @staticmethod
    def get_recent_logs(db: Session, limit: int = 50, action: Optional[str] = None, username: Optional[str] = None):
        query = db.query(AuditLog).order_by(AuditLog.created_at.desc())

        if action:
            query = query.filter(AuditLog.action == action)
        if username:
            query = query.filter(AuditLog.username == username)

        return query.limit(limit).all()
