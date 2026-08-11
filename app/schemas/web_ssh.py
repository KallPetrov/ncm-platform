from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class SSHSessionBase(BaseModel):
    device_id: int


class SSHSessionCreate(SSHSessionBase):
    pass


class SSHSessionResponse(SSHSessionBase):
    id: int
    user_id: int
    session_token: str
    status: str
    started_at: datetime
    closed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class KeystrokeLogBase(BaseModel):
    ssh_session_id: int
    typed_command: str
    output_sample: Optional[str] = None


class KeystrokeLogCreate(KeystrokeLogBase):
    pass


class KeystrokeLogResponse(KeystrokeLogBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
