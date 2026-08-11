# Changelog

All notable changes to the NCM Platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.0] - 2026-08-09

### Added
- Implemented **Secrets Vault & Password Rotation Service** (`app/services/secrets_vault.py`) providing Fernet dynamic symmetric encryption at rest and automated credential rotation workflow.
- Implemented **NetBox / Nautobot SSOT Synchronization Service** (`app/services/ssot_sync.py`) for importing/exporting devices and metadata from Single Source of Truth database.
- Implemented **Basic Network Monitoring & Topology Mapping Service** (`app/services/topology.py`) utilizing LLDP/CDP neighbor discovery and topological edge construction.
- Implemented **AI-Assisted Configuration Analysis & Anomaly Detection** (`app/services/ai_analysis.py`) offering natural Bulgarian language explanations of diffs and heuristics-based security scans.
- Added comprehensive unit and integration tests inside `tests/test_advanced_modules.py` passing with 100% success.
- Updated `Module_Status.md` tracking 100% completion of all listed modules.

## [0.8.0] - 2026-08-09

### Added
- Fully implemented **Built-in Web Terminal & Session Recording** (`app/services/web_ssh.py`, `app/api/web_ssh.py`, `app/models/web_ssh.py`) for complete PAM terminal management.
- Implemented secure token-based SSH Session establishment (Network PAM Proxy) hiding plain credentials from the client side.
- Developed real-time command / keystroke capture and output-logging engine (Keystroke Logging) for audits and compliance.
- Restored admin-only secure restrictions for viewing and reviewing terminal logs.
- Added automated backend unit and integration tests inside `tests/test_web_ssh.py` with 100% success.

## [0.7.0] - 2026-08-09

### Added
- Completed auditing and mapping 100% of all listed core and extended modules in `Module_Status.md` for complete product transparency.
- Fully implemented **Configuration Validation** (`app/services/config_validation.py`) supporting pre-push syntax validations, multiplatform reachability validations, and operational state comparisons.
- Added API endpoint `/configurations/validate-commands` allowing on-demand checks on devices prior to configuration updates.
- Added integration unit and component tests inside `tests/test_config_validation.py` passing with 100% success.

## [0.6.0] - 2026-08-09

### Added
- Fully implemented **Firmware / OS Upgrade Automation** (`app/services/firmware_upgrade.py`, `app/api/firmware.py`, `app/models/firmware.py`) with models, schemas, database registration, and automatic pre-checks/post-checks.
- Automated pre-checks verifying target version mismatch and calculating free storage space.
- Automatic verification of firmware images using MD5/SHA256 checksum check on the destination device.
- Automated system restart (reload) and a connection retry wait loop to check post-install status.
- Automatic rollback / fallback trigger that reverts the boot image if post-checks fail or connection timeout occurs.
- Implemented `/firmware/images` upload, `/firmware/upgrade` start, and `/firmware/jobs/{job_id}` status query endpoints.
- Developed comprehensive automated backend unit and integration tests inside `tests/test_firmware_upgrade.py`.

## [0.5.0] - 2026-08-09

### Added
- Fully implemented **Config Data Sanitization & Redaction Engine** (`app/services/sanitization.py`) utilizing robust, multi-vendor regex-based matching to securely strip, mask, and redact sensitive attributes from backups.
- Automatically handles redaction of Cisco-style secrets and passwords, Juniper-style encrypted secrets, Pre-Shared Keys (PSKs/IKE/IPsec), SNMP communities, SSH keys, and PEM-formatted Private Keys.
- Integrated `SanitizationService` directly into `BackupEngine.perform_backup` to automatically sanitize configurations immediately upon retrieval from devices, ensuring no plain secrets reach the database or Git storage.
- Created `/configurations/sanitize` API endpoint allowing secure preview and manually testing configuration sanitization.
- Implemented automated backend unit and integration tests inside `tests/test_sanitization.py` with 100% success.

## [0.4.9] - 2026-08-09

### Added
- Real backend password reset endpoint `/auth/reset-password` in `app/api/auth.py` with email validation, database verification, dynamic hash generation, and full audit logging
- Expanded `LoginForm.tsx` UI supporting seamless switching between standard "Sign In", "Register Account", and "Reset Password" views with full validation, integration, and user-friendly success notifications
- Created integration unit test `test_reset_password` inside `tests/test_auth.py` verifying full recovery flows

## [0.4.8] - 2026-08-09

### Added
- Expanded Pydantic schema `BackupJobListItem` in `app/schemas/backup_job.py` to include real `device_name` and `error_message` fields
- Enhanced backend backup jobs endpoint `/backup-jobs/` in `app/api/backup_jobs.py` to dynamically fetch device names through SQLAlchemy relationships and output real error details
- Fully integrated frontend `BackupJobsDashboard.tsx` with backend contracts, displaying real device names, starting/completion timestamps, and error reasons for failed backups

## [0.4.7] - 2026-08-09

### Added
- Multi-platform Docker configuration containing `Dockerfile` for FastAPI backend, `frontend/Dockerfile` for Vite compilation, and `frontend/nginx.conf` for serving assets with Single Page Application routing
- Complete `docker-compose.yml` orchestrating PostgreSQL, Redis, FastAPI backend, Celery worker, and Nginx frontend
- Added container entrypoint shell script `entrypoint.sh` with a native socket-based PostgreSQL wait loop, automatic database initialization (`scripts/init_db.py`), tables migration, default admin credentials seeding, and Git configurations setup
- Detailed multi-platform Docker guides and startup commands added to `README.md`

## [0.4.6] - 2026-08-09

### Added
- Dynamic Configuration Viewer with device selection and download functionality, eliminating any hardcoded variables
- Real Backend Settings Panel with PostgreSQL and Redis live connection testing and configurations persistence in `storage/settings.json`
- Real API endpoints and integration for System Settings under `/settings/` with complete RBAC enforcement and audit trail recording
- New suite of integration tests for system settings verifying auth, endpoints, and updates in `tests/test_settings.py`

### Fixed
- Fixed missing `datetime` import in notification service to prevent runtime crashes
- Created robust `conftest.py` setup to clean the SQLite test database before every test run, fixing all regression test failures

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
