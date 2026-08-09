from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class AuditLogBase(BaseModel):
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None


class AuditLogInDB(AuditLogBase):
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLog(AuditLogInDB):
    pass
