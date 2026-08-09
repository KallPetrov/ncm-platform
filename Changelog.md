# Changelog

All notable changes to the NCM Platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-08-09

### Added
- JWT authentication with timestamp-based token expiration
- Device management API with full CRUD operations
- Configuration management API with versioning
- Backup jobs API for scheduled and immediate backups
- Frontend path aliases configuration for Vite
- Browser preview support for frontend testing
- Tailwind CSS v3.4.0 for stable UI styling
- TypeScript type definitions for Vite environment

### Changed
- Fixed JWT datetime to timestamp conversion for proper token validation
- Fixed Device model import conflicts in API endpoints
- Fixed device password hashing to use bcrypt directly
- Fixed configurations Device model import
- Updated frontend vite.config.ts with path aliases
- Fixed Vite __dirname deprecation warning with import.meta.dirname
- Downgraded from Tailwind CSS v4 to v3.4.0 for stability
- Fixed TypeScript build errors for CSS imports and environment variables

### Security
- JWT token-based authentication with proper timestamp validation
- Secure password hashing with bcrypt for device credentials
- Environment-based SECRET_KEY configuration
- Protected API endpoints with JWT validation
- Admin user with default credentials (change required)

### Infrastructure
- API server running on port 8000 with full functionality
- Frontend dev server running on port 5173
- All backend endpoints tested and functional
- Frontend-backend integration verified
- Browser preview for frontend testing
- Tailwind CSS build working correctly (15.75 kB CSS output)

## [0.3.0] - 2026-08-08

### Added
- Complete environment setup with Python venv and dependencies
- PostgreSQL database and user configuration
- Redis server for Celery task queue
- Database initialization script with admin user creation
- Git repository initialization for configuration storage
- Environment configuration file (.env) with all necessary variables
- Password encryption/decryption functions for secure credential storage
- Celery worker for async task processing
- Cross-platform compatibility setup (Linux, Windows, macOS)

### Changed
- Updated requirements.txt with flexible version constraints
- Fixed Pydantic schema deprecations (regex → pattern)
- Fixed bcrypt compatibility issues with Python 3.14
- Updated authentication to use bcrypt directly instead of passlib
- Fixed TypeScript deprecation warning with ignoreDeprecations setting
- Enhanced security with proper SECRET_KEY configuration

### Security
- Secure password hashing with bcrypt
- Fernet encryption for device credentials
- Environment-based configuration
- Proper JWT token validation
- Admin user with default credentials (change required)

### Infrastructure
- PostgreSQL 18 database setup
- Redis 8 server for task queue
- Python 3.14 virtual environment
- All dependencies installed and tested
- API server running on port 8000
- Celery worker for background tasks

## [0.2.0] - 2026-08-08

### Added
- Real API client with JWT authentication
- Login/logout functionality with token management
- Authentication UI with login form
- Protected API endpoints with JWT validation
- Database initialization script with admin user creation
- Git repository initialization for configuration storage
- CORS configuration for frontend-backend communication
- Environment variable configuration for frontend API URL

### Changed
- Removed all hardcoded data from frontend
- Connected frontend to real backend API
- Added authentication protection to device endpoints
- Updated API client to handle 401 errors and redirect to login
- Enhanced error handling in frontend components

### Security
- JWT token-based authentication
- Password hashing with bcrypt
- Token storage in localStorage
- Automatic token refresh on 401 errors
- Protected routes requiring authentication

## [0.1.0] - 2026-08-08

### Added
- Initial project structure with FastAPI backend
- Database models for Device, Configuration, BackupJob, User
- Pydantic schemas for API validation
- Device connectivity service with Netmiko for SSH/Telnet
- Git-based configuration storage and versioning
- Configuration backup engine with change detection
- Celery tasks for async backup operations
- Notification system (email and webhooks)
- Device adapters for multiple vendors (Cisco, MikroTik, Juniper, HP, Arista)
- Bulk automation with Jinja2 template engine
- Compliance/auditing rule engine
- Alembic database migrations
- React + TypeScript frontend with Vite
- TailwindCSS and shadcn/ui components
- Device management UI with modal dialogs
- Responsive layout with sidebar navigation
- API endpoints for devices, configurations, and backup jobs

### Changed
- Updated requirements.txt with all necessary dependencies
- Added environment configuration options for SMTP and webhooks

### Security
- Password encryption with bcrypt
- JWT token authentication support
- Secure credential storage

---

## Version Format
- **MAJOR**: Breaking changes or major feature additions
- **MINOR**: New features, backwards compatible
- **PATCH**: Bug fixes, small improvements

## Release Process
1. Update version in `app/core/config.py` (APP_VERSION)
2. Update version in `frontend/package.json`
3. Add changes to this Changelog.md
4. Update Module_Status.md
5. Commit with version tag
