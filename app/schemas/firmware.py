from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class FirmwareImageBase(BaseModel):
    filename: str
    version: str
    device_type: str
    vendor: str
    md5_hash: str
    file_size: int
    file_path: str


class FirmwareImageCreate(FirmwareImageBase):
    pass


class FirmwareImageResponse(FirmwareImageBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UpgradeJobBase(BaseModel):
    device_id: int
    firmware_image_id: int


class UpgradeJobCreate(UpgradeJobBase):
    pass


class UpgradeJobResponse(UpgradeJobBase):
    id: int
    status: str
    pre_check_results: Optional[str] = None
    post_check_results: Optional[str] = None
    error_message: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
