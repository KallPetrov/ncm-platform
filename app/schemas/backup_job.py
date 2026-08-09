from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class BackupJobStatus(str):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class BackupJobBase(BaseModel):
    device_id: int
    status: str = "pending"


class BackupJobCreate(BackupJobBase):
    pass


class BackupJobUpdate(BaseModel):
    status: Optional[str] = None
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None


class BackupJobInDB(BackupJobBase):
    id: int
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BackupJob(BackupJobInDB):
    pass


class BackupJobListItem(BaseModel):
    id: int
    device_id: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BackupJobSummary(BaseModel):
    total_jobs: int
    pending: int
    running: int
    success: int
    failed: int
