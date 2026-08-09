from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json
import os
from pathlib import Path
from app.core.database import get_db
from app.models.user import User
from app.api.auth import get_current_active_user, require_permission
from app.schemas.settings import SystemSettingsSchema
from app.services.audit import AuditService

router = APIRouter(prefix="/settings", tags=["settings"])

SETTINGS_FILE_PATH = Path("storage/settings.json")

DEFAULT_SETTINGS = {
    "db_url": "postgresql://ncm_user:ncm_password@localhost:5432/ncm_db",
    "redis_url": "redis://localhost:6379/0",
    "enable_email": False,
    "email_smtp": "smtp.example.com",
    "email_port": "587",
    "session_timeout": "30",
    "max_login_attempts": "5",
    "api_timeout": "30",
    "max_concurrent_backups": "10"
}


def load_settings_from_file() -> dict:
    if not SETTINGS_FILE_PATH.exists():
        # Ensure directories exist
        SETTINGS_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_FILE_PATH, "w") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)
        return DEFAULT_SETTINGS
    try:
        with open(SETTINGS_FILE_PATH, "r") as f:
            data = json.load(f)
            # Merge with default settings to ensure all keys exist
            merged = DEFAULT_SETTINGS.copy()
            merged.update(data)
            return merged
    except Exception:
        return DEFAULT_SETTINGS


def save_settings_to_file(settings_data: dict):
    SETTINGS_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE_PATH, "w") as f:
        json.dump(settings_data, f, indent=4)


@router.get("/", response_model=SystemSettingsSchema)
def get_settings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get system settings. Restricted to authenticated users."""
    # Ensure user has access/permissions
    require_permission(current_user, "manage_devices", db=db, resource_type="settings")
    return load_settings_from_file()


@router.put("/", response_model=SystemSettingsSchema)
def update_settings(
    settings_payload: SystemSettingsSchema,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update system settings. Restricted to authenticated users with manage permissions."""
    require_permission(current_user, "manage_devices", db=db, resource_type="settings")

    settings_dict = settings_payload.model_dump()
    save_settings_to_file(settings_dict)

    # Audit logging for security compliance
    AuditService.log_action(
        db,
        current_user,
        "settings_updated",
        resource_type="settings",
        resource_id=0,
        details="System configurations and preferences updated"
    )

    return settings_dict


@router.post("/test-connection/{connection_type}")
def test_connection(
    connection_type: str,
    payload: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Test connection to PostgreSQL or Redis dynamically."""
    require_permission(current_user, "manage_devices", db=db, resource_type="settings")

    if connection_type.lower() == "postgresql":
        # In a real setup, we would try to connect using sqlalchemy engine
        url = payload.get("url")
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        try:
            from sqlalchemy import create_engine
            # Use quick timeout connection
            test_engine = create_engine(url, connect_args={"connect_timeout": 3} if url.startswith("postgres") else {})
            with test_engine.connect() as conn:
                pass
            return {"success": True, "message": "Successfully connected to PostgreSQL database"}
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"PostgreSQL connection failed: {str(e)}"
            )

    elif connection_type.lower() == "redis":
        url = payload.get("url")
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        try:
            from redis import Redis
            r = Redis.from_url(url, socket_timeout=3)
            r.ping()
            return {"success": True, "message": "Successfully connected to Redis server"}
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Redis connection failed: {str(e)}"
            )
    else:
        raise HTTPException(status_code=400, detail="Invalid connection type. Supported types: postgresql, redis")
