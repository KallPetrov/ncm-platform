from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class SSHSession(Base):
    __tablename__ = "ssh_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)

    session_token = Column(String(255), unique=True, index=True, nullable=False)
    status = Column(String(50), default="active")  # active, closed, disconnected

    started_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    keystroke_logs = relationship("KeystrokeLog", back_populates="ssh_session", cascade="all, delete-orphan")
    device = relationship("Device")
    user = relationship("User")


class KeystrokeLog(Base):
    __tablename__ = "keystroke_logs"

    id = Column(Integer, primary_key=True, index=True)
    ssh_session_id = Column(Integer, ForeignKey("ssh_sessions.id"), nullable=False)

    typed_command = Column(Text, nullable=False)     # Recorded commands executed
    output_sample = Column(Text, nullable=True)     # Sample output for troubleshooting

    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    ssh_session = relationship("SSHSession", back_populates="keystroke_logs")
