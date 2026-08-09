from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from datetime import datetime
from typing import Optional
from enum import Enum


class DeviceType(str, Enum):
    ROUTER = "router"
    SWITCH = "switch"
    FIREWALL = "firewall"
    WIRELESS = "wireless"
    LOAD_BALANCER = "load_balancer"
    OTHER = "other"


class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"
    MAINTENANCE = "maintenance"


class ConnectionProtocol(str, Enum):
    SSH = "ssh"
    TELNET = "telnet"


class DeviceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    ip_address: str = Field(..., pattern=r'^[\d\.:]+$')
    device_type: DeviceType = DeviceType.OTHER
    vendor: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    connection_protocol: ConnectionProtocol = ConnectionProtocol.SSH
    port: int = Field(22, ge=1, le=65535)
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1)
    enable_password: Optional[str] = None
    status: DeviceStatus = DeviceStatus.UNKNOWN
    backup_interval: int = Field(3600, ge=60)
    auto_backup_enabled: bool = True
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=255)
    tags: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_connection_protocol(cls, values):
        if isinstance(values, dict):
            if "connection_protocol" not in values and "protocol" in values:
                values["connection_protocol"] = values.pop("protocol")
        return values

    @field_validator('ip_address')
    @classmethod
    def validate_ip_address(cls, v):
        import ipaddress
        try:
            ipaddress.ip_address(v)
        except ValueError as exc:
            raise ValueError('Invalid IP address') from exc
        return v


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    ip_address: Optional[str] = Field(None, pattern=r'^[\d\.:]+$')
    device_type: Optional[DeviceType] = None
    vendor: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    connection_protocol: Optional[ConnectionProtocol] = None
    port: Optional[int] = Field(None, ge=1, le=65535)
    username: Optional[str] = Field(None, min_length=1, max_length=100)
    password: Optional[str] = Field(None, min_length=1)
    enable_password: Optional[str] = None
    status: Optional[DeviceStatus] = None
    backup_interval: Optional[int] = Field(None, ge=60)
    auto_backup_enabled: Optional[bool] = None
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=255)
    tags: Optional[str] = None

    @field_validator('ip_address')
    @classmethod
    def validate_ip_address(cls, v):
        if v is not None:
            import ipaddress
            try:
                ipaddress.ip_address(v)
            except ValueError as exc:
                raise ValueError('Invalid IP address') from exc
        return v


class DeviceInDB(DeviceBase):
    id: int
    last_backup: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Device(DeviceInDB):
    pass


class DeviceListItem(BaseModel):
    id: int
    name: str
    ip_address: str
    device_type: DeviceType
    vendor: Optional[str]
    status: DeviceStatus
    connection_protocol: ConnectionProtocol
    last_backup: Optional[datetime] = None
    auto_backup_enabled: bool

    model_config = ConfigDict(from_attributes=True)


class DeviceConnectionTest(BaseModel):
    device_id: int
    success: bool
    connected: bool
    latency_ms: Optional[float] = None
    error_message: Optional[str] = None
    error: Optional[str] = None
