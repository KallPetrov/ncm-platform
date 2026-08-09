from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class DeviceType(str, enum.Enum):
    ROUTER = "router"
    SWITCH = "switch"
    FIREWALL = "firewall"
    WIRELESS = "wireless"
    LOAD_BALANCER = "load_balancer"
    OTHER = "other"


class DeviceStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    UNKNOWN = "unknown"
    MAINTENANCE = "maintenance"


class ConnectionProtocol(str, enum.Enum):
    SSH = "ssh"
    TELNET = "telnet"


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False, index=True)
    device_type = Column(Enum(DeviceType), default=DeviceType.OTHER)
    vendor = Column(String(100))
    model = Column(String(100))

    # Connection settings
    connection_protocol = Column(String(20), nullable=False, default=ConnectionProtocol.SSH.value)
    port = Column(Integer, default=22)
    username = Column(String(100), nullable=False)
    password = Column(Text, nullable=False)  # Will be encrypted
    enable_password = Column(Text, nullable=True)  # Will be encrypted

    # Status
    status = Column(Enum(DeviceStatus), default=DeviceStatus.UNKNOWN)
    last_backup = Column(DateTime(timezone=True), nullable=True)
    last_seen = Column(DateTime(timezone=True), nullable=True)

    # Backup settings
    backup_interval = Column(Integer, default=3600)  # seconds
    auto_backup_enabled = Column(Boolean, default=True)

    # Metadata
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    tags = Column(Text, nullable=True)  # JSON string of tags

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    configurations = relationship("Configuration", back_populates="device", cascade="all, delete-orphan")
    backup_jobs = relationship("BackupJob", back_populates="device", cascade="all, delete-orphan")

    @property
    def protocol(self):
        if isinstance(self.connection_protocol, ConnectionProtocol):
            return self.connection_protocol
        if self.connection_protocol:
            return ConnectionProtocol(self.connection_protocol)
        return ConnectionProtocol.SSH

    @protocol.setter
    def protocol(self, value):
        if isinstance(value, ConnectionProtocol):
            self.connection_protocol = value.value
        else:
            self.connection_protocol = value


class Configuration(Base):
    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=True)
    config_hash = Column(String(64), nullable=True, index=True)
    file_path = Column(String(512), nullable=True)  # Path in git repo
    file_size = Column(Integer, nullable=True)

    # Change detection
    is_changed = Column(Boolean, default=False)
    change_summary = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    device = relationship("Device", back_populates="configurations")

    def __init__(self, *args, **kwargs):
        content = kwargs.pop("content", None)
        if content is not None:
            kwargs["content"] = content
            kwargs.setdefault("config_hash", self._hash_content(content))
            kwargs.setdefault("file_path", f"/tmp/config_v{kwargs.get('version', 1)}.txt")
            kwargs.setdefault("file_size", len(content.encode("utf-8")))
        super().__init__(*args, **kwargs)

    @staticmethod
    def _hash_content(content: str) -> str:
        import hashlib
        return hashlib.sha256(content.encode("utf-8")).hexdigest()


class BackupJob(Base):
    __tablename__ = "backup_jobs"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    status = Column(String(50), default="pending")  # pending, running, success, failed
    error_message = Column(Text, nullable=True)
    scheduled_time = Column(String(50), nullable=True)

    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    device = relationship("Device", back_populates="backup_jobs")
