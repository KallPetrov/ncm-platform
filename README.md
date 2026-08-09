# NCM Platform - Network Configuration Management

**Version:** 0.4.0  
**Status:** Development Phase  
**Last Updated:** 2026-08-09

Self-hosted Network Configuration Management platform inspired by Unimus. Built for production use with real functionality, no simulated data, and cross-platform compatibility.
## Features

- **Network Automation**: Mass Config Push/Pull capabilities for bulk configuration management across multiple devices
- **Disaster Recovery**: Comprehensive network configuration backup with automated scheduling and version control
- **Configuration Change Detection**: Real-time detection and management of configuration changes with detailed diff analysis
- **Change Management**: Complete change tracking, approval workflows, and rollback capabilities
- **Network-wide Configuration Auditing**: Advanced auditing capabilities for compliance checking and security validation
- **Configuration Backup**: Automated scheduled backups for network devices with Git-based versioning
- **Multi-vendor Support**: Support for 450+ device types from 160+ vendors (Cisco, MikroTik, Juniper, HP, Arista and more)
- **Modern UI**: React-based interface with modal dialogs and responsive design
- **Real-time Notifications**: Email and webhook support for critical events
- **Compliance Reporting**: Ensure compliance with internal policies and industry standards

## Tech Stack

### Backend
- Python 3.11+
- FastAPI (Web framework)
- PostgreSQL (Database)
- Netmiko (SSH/Telnet connectivity)
- Celery + Redis (Task queue & scheduler)
- Git (Configuration versioning)
- Jinja2 (Template engine)

### Frontend
- React + TypeScript
- Vite (Build tool)
- TailwindCSS (Styling)
- shadcn/ui (UI components)
- Lucide Icons

## Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+

### Backend Setup

```bash
# Clone repository
git clone <repository-url>
cd ncm-platform

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration (database, redis, smtp, etc.)

# Run database migrations
alembic upgrade head

# Start Redis (required for Celery)
redis-server

# Start Celery worker (in separate terminal)
celery -A app.tasks.celery_app worker --loglevel=info

# Start API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Production Setup

```bash
# Build frontend
cd frontend
npm run build

# Start backend with production settings
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Project Structure

```
ncm-platform/
├── app/
│   ├── api/              # API endpoints (devices, configurations, backup_jobs)
│   ├── core/             # Configuration & security
│   ├── models/           # Database models (Device, Configuration, BackupJob, User)
│   ├── schemas/          # Pydantic schemas for validation
│   ├── services/         # Business logic (connectivity, backup, automation, compliance)
│   ├── tasks/            # Celery tasks for async operations
│   └── main.py           # FastAPI application
├── alembic/              # Database migrations
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── lib/          # Utilities
│   │   └── App.tsx       # Main application
│   └── package.json
├── storage/              # Git repository for configs
├── tests/                # Test suite
├── Changelog.md          # Version history
├── Module_Status.md      # Development progress
└── README.md             # This file
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development Status

See [Module_Status.md](Module_Status.md) for detailed progress tracking.

### Current Status (v0.1.0)
- Backend core functionality implemented
- Frontend UI framework setup
- Device management with modal dialogs
- Frontend-backend integration pending
- Authentication system pending
- Real database setup pending

## Cross-Platform Compatibility

The platform is designed to work on:
- **Linux** (Ubuntu, Debian, CentOS, RHEL)
- **Windows** (Windows 10/11, Windows Server)
- **macOS** (Intel and Apple Silicon)

### Platform-Specific Notes

**Linux:**
- Use system package manager for dependencies
- Consider systemd for service management

**Windows:**
- Use WSL2 for best experience
- Native Windows support available

**macOS:**
- Homebrew recommended for dependencies
- Native macOS support available

## Contributing

1. Follow the development plan in Module_Status.md
2. Update Changelog.md for any changes
3. Update version numbers for releases
4. Ensure no hardcoded data
5. Test cross-platform compatibility

## Versioning

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes

See [Changelog.md](Changelog.md) for version history.

## License

**Commercial License**

This software is proprietary and licensed for commercial use. All rights reserved.

### License Terms
- This software is licensed, not sold
- Use requires a valid commercial license
- Redistribution and modification are prohibited without explicit permission
- Support and updates are provided under the license agreement

### Licensing Information
For licensing inquiries, please contact the platform provider.

**© 2026 NCM Platform. All rights reserved.**

## Support

For issues and questions, please refer to:
- Module_Status.md for current development status
- Changelog.md for recent changes
- API documentation at /docs endpoint
