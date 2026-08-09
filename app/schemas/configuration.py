from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ConfigurationBase(BaseModel):
    device_id: int
    version: int
    config_hash: str
    file_path: str
    file_size: int
    is_changed: bool = False
    change_summary: Optional[str] = None


class ConfigurationCreate(ConfigurationBase):
    pass


class ConfigurationUpdate(BaseModel):
    is_changed: Optional[bool] = None
    change_summary: Optional[str] = None


class ConfigurationInDB(ConfigurationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Configuration(ConfigurationInDB):
    pass


class ConfigurationListItem(BaseModel):
    id: int
    device_id: int
    version: int
    config_hash: str
    file_size: int
    is_changed: bool
    change_summary: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConfigurationDiff(BaseModel):
    device_id: int
    version_a: int
    version_b: int
    diff_output: str
    summary: Optional[str] = None
