from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class FirmwareImage(Base):
    __tablename__ = "firmware_images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    version = Column(String(100), nullable=False)
    device_type = Column(String(100), nullable=False)  # e.g., router, switch, firewall
    vendor = Column(String(100), nullable=False)       # e.g., Cisco, Juniper
    md5_hash = Column(String(64), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(512), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    upgrade_jobs = relationship("UpgradeJob", back_populates="firmware_image", cascade="all, delete-orphan")


class UpgradeJob(Base):
    __tablename__ = "upgrade_jobs"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    firmware_image_id = Column(Integer, ForeignKey("firmware_images.id"), nullable=False)
    status = Column(String(50), default="pending")  # pending, running, success, failed, rolled_back

    pre_check_results = Column(Text, nullable=True)   # JSON string or text details
    post_check_results = Column(Text, nullable=True) # JSON string or text details
    error_message = Column(Text, nullable=True)

    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    firmware_image = relationship("FirmwareImage", back_populates="upgrade_jobs")
    device = relationship("Device")
