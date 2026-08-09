# Changelog

All notable changes to the NCM Platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.5] - 2026-08-09

### Added
- Full project documentation refresh covering the current backend and frontend implementation status
- A clearer project overview with implementation highlights, quick-start instructions, and verification notes

### Changed
- Updated the repository info files to reflect the completed audit logging, RBAC checks, compliance UI, and frontend integration work
- Bumped backend and frontend versions to 0.4.5 for the documentation and project-state refresh

### Testing
- Verified backend regression coverage for audit, RBAC, devices, and configurations remains passing
- Verified frontend production build remains successful

## [0.4.4] - 2026-08-09

### Added
- A richer compliance reporting view with summary cards and manual refresh controls in the frontend

### Changed
- Improved the compliance tab experience for faster review of device posture and rule status
- Updated project version metadata across backend and frontend

### Testing
- Verified frontend production build remains successful

## [0.4.3] - 2026-08-09

### Added
- Initial audit logging service and audit-log API for tracking platform activity
- RBAC-aware audit-log access restricted to administrative users
- Regression tests covering audit-log visibility and device-creation logging

### Changed
- Wired audit logging into device create/update/delete/backup and configuration delete flows
- Exported audit and device models from the model package to support initialization and testing
- Updated project version metadata across backend and frontend

### Testing
- Verified new audit/RBAC pytest cases pass
- Verified frontend production build remains successful

## [0.4.2] - 2026-08-09

### Added
- New automation API endpoints for template listing, validation, and execution against devices
- New change-management API endpoint for per-device configuration change analysis
- Compliance reports UI tab with real backend-backed compliance results
- Frontend API client helpers for compliance and automation workflows

### Changed
- Registered automation and change-management routers in the FastAPI app
- Fixed configuration content persistence so change detection can compare real stored versions
- Standardized change-detection responses to expose a consistent has_changes field
- Updated frontend shell to surface a dedicated compliance section

### Testing
- Verified 4 automation/change-management pytest cases pass
- Verified frontend production build succeeds

## [0.4.1] - 2026-08-09

### Added
- Backend regression coverage for device, configuration, and integration workflows
- A real configuration compliance endpoint for evaluating device configurations against built-in security rules
- A dashboard overview API and UI module showing device, configuration, backup, and compliance summaries

### Changed
- Stabilized device and configuration APIs to match the expected request and response contracts
- Added compatibility for maintenance device status and connection-test payloads
- Relaxed test database state handling to avoid duplicate-device fixture collisions
- Updated project version metadata and documentation to reflect the current implementation state

### Testing
- Verified 37 backend pytest cases pass in local SQLite-backed test mode

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
