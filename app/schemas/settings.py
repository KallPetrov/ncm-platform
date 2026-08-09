from pydantic import BaseModel
from typing import Optional

class SystemSettingsSchema(BaseModel):
    # Database settings
    db_url: str
    redis_url: str

    # Notification settings
    enable_email: bool
    email_smtp: str
    email_port: str

    # Security settings
    session_timeout: str
    max_login_attempts: str

    # Network settings
    api_timeout: str
    max_concurrent_backups: str
