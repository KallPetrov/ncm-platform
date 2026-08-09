from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class ConfigurationBase(BaseModel):
    device_id: int
    version: int
    content: Optional[str] = None
    config_hash: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
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

    model_config = ConfigDict(from_attributes=True)


class Configuration(ConfigurationInDB):
    pass


class ConfigurationListItem(BaseModel):
    id: int
    device_id: int
    version: int
    content: Optional[str] = None
    config_hash: Optional[str] = None
    file_size: Optional[int] = None
    is_changed: bool
    change_summary: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConfigurationDiff(BaseModel):
    device_id: int
    version_a: int
    version_b: int
    diff_output: Optional[str] = None
    summary: Optional[str] = None
