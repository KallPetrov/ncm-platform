# NCM Platform - Network Configuration Management

**Version:** 0.6.0
**Status:** Development Phase  
**Last Updated:** 2026-08-09

Self-hosted Network Configuration Management platform inspired by Unimus. Built for real-world use with backend APIs, database-backed device management, compliance reporting, automation workflows, and audit logging.

## What is implemented

The project now includes a working end-to-end foundation for network configuration management:

- **Firmware / OS Upgrade Automation** - Fully automated, schedule-driven firmware and operating system upgrades on network devices. Includes robust pre-checks (disk space, target version verification), MD5 checksum verification, and automatic rollback triggers upon failure or timeout.
- **Config Data Sanitization & Redaction Engine** - Real-time regex-based detection and masking of sensitive credentials (passwords, enable secrets, Pre-Shared Keys, private keys, SNMP communities) from the retrieved backups.
- Device lifecycle management with CRUD operations and backup triggering
- Configuration versioning and real configuration inspection
- Compliance evaluation with report summaries and rule-level details
- Automation workflows with template validation and execution support
- Dashboard summaries for devices, backups, configurations, and compliance
- Audit logging with role-aware records and admin-restricted audit access
- Frontend integration with a React + TypeScript UI backed by the real API
- Dynamic Configuration Viewer with device selection and download functionality
- Real Backend Settings Panel with PostgreSQL and Redis live connection testing and settings persistence

## Current feature status

### Backend
- FastAPI application with authenticated API endpoints
- SQLite-based local testing mode and PostgreSQL-ready configuration
- Device, configuration, backup job, user, and audit models
- RBAC-aware permission checks for privileged actions
- Audit trail support for mutation and permission-denied events

### Frontend
- React + TypeScript + Vite application
- Protected authentication flow
- Device management UI
- Configuration and compliance views
- Automation and backup job panels
- Audit Logs tab with filtering and role display

## Tech stack

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy
- Pydantic
- SQLite for local testing, PostgreSQL-ready for production
- Netmiko-style connectivity abstraction
- Celery + Redis support for async workflows
- Git-based storage concepts for configuration versioning

### Frontend
- React + TypeScript
- Vite
- TailwindCSS
- shadcn/ui-inspired components
- Lucide Icons

## Quick start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Optional: PostgreSQL and Redis for production-like deployments

### Backend

```bash
cd /home/kallata/Downloads/ncm-platform
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
TESTING=1 uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker (Recommended - Cross-platform)

The easiest way to run the entire platform with PostgreSQL, Redis, and Celery background workers is using Docker Compose:

```bash
# Build and start all services in the background
docker compose up --build -d

# Check status of the running containers
docker compose ps

# View logs for all services
docker compose logs -f
```

Once running, access the services on your host machine:
- **Frontend Web UI:** http://localhost:3000
- **API Swagger Docs:** http://localhost:8000/docs
- **Default Login:** `admin` / `admin` (change immediately in production!)

### Tests

```bash
cd /home/kallata/Downloads/ncm-platform
TESTING=1 ./.venv/bin/python -m pytest -q tests/test_audit_rbac.py tests/test_devices.py tests/test_configurations.py
```

## Project structure

```text
ncm-platform/
├── app/
│   ├── api/              # FastAPI routes for auth, devices, configs, backups, audit
│   ├── core/             # Settings, DB, security helpers
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic request/response schemas
│   ├── services/         # Business logic for compliance, automation, backup, audit
│   └── main.py           # Application entrypoint
├── frontend/             # React frontend
├── tests/                # Backend regression tests
├── Changelog.md          # Version history
├── Module_Status.md      # Detailed module progress
└── README.md             # Project overview
```

## API documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Current status (v0.4.5)

Verified in the current workspace:
- Backend regression tests for audit/RBAC, devices, and configurations are passing
- Frontend production build completes successfully
- Compliance, automation, backup, and audit views are wired to the real backend API

## Contributing

1. Keep the module plan in Module_Status.md aligned with implementation
2. Update Changelog.md for every meaningful change
3. Bump the version when shipping new functionality or fixes
4. Keep the backend and frontend contracts synchronized

## License

Commercial license. All rights reserved.
