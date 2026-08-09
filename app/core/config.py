from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://ncm_user:ncm_password@localhost:5432/ncm_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "ncm-platform-secret-key-2026-production-ready"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Git Storage
    GIT_REPO_PATH: str = "./storage/configs"
    
    # Application
    APP_NAME: str = "NCM Platform"
    APP_VERSION: str = "0.4.8"
    DEBUG: bool = True
    
    # Backup Settings
    DEFAULT_BACKUP_INTERVAL: int = 3600  # 1 hour in seconds
    MAX_CONCURRENT_BACKUPS: int = 10
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
