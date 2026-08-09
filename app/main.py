from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import devices, configurations, backup_jobs, auth, users, dashboard, automation, change_management, audit_logs, settings as api_settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="NCM Platform API for Network Configuration Management"
)

# Log SECRET_KEY for debugging
logger.info(f"SECRET_KEY loaded: {settings.SECRET_KEY[:20]}...")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(devices.router)
app.include_router(configurations.router)
app.include_router(backup_jobs.router)
app.include_router(dashboard.router)
app.include_router(automation.router)
app.include_router(change_management.router)
app.include_router(audit_logs.router)
app.include_router(api_settings.router)


@app.get("/")
def read_root():
    return {"message": "NCM Platform API", "version": settings.APP_VERSION}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
