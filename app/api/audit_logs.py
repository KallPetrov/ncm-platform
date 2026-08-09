from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.auth import get_current_admin_user
from app.models.user import User
from app.schemas.audit import AuditLog as AuditLogSchema
from app.services.audit import AuditService

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


@router.get("/", response_model=List[AuditLogSchema])
def list_audit_logs(
    limit: int = 50,
    action: Optional[str] = None,
    username: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    return AuditService.get_recent_logs(db, limit=limit, action=action, username=username)
