#!/usr/bin/env python3
"""
Database initialization script for NCM Platform
Creates the database, runs migrations, and creates initial admin user
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.core.database import Base, SessionLocal
from app.models.user import User
from app.models.device import Device, Configuration, BackupJob
import bcrypt


def create_storage_directories():
    """Create necessary storage directories"""
    storage_path = Path(settings.GIT_REPO_PATH)
    storage_path.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created storage directory: {storage_path}")


def init_database():
    """Initialize database with tables"""
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")
    engine.dispose()


def create_admin_user():
    """Create initial admin user"""
    db = SessionLocal()
    try:
        # Check if admin user already exists
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            print("✓ Admin user already exists")
            return
        
        # Create admin user
        password = "admin"
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        admin_user = User(
            username="admin",
            email="admin@ncm-platform.local",
            hashed_password=hashed_password,  # Default password - change this!
            is_active=True,
            is_admin=True
        )
        db.add(admin_user)
        db.commit()
        print("✓ Admin user created (username: admin, password: admin)")
        print("  ⚠️  IMPORTANT: Change the default admin password immediately!")
    except Exception as e:
        print(f"✗ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()


def init_git_repository():
    """Initialize Git repository for configuration storage"""
    import subprocess
    storage_path = Path(settings.GIT_REPO_PATH)
    
    try:
        # Check if already a git repository
        git_dir = storage_path / ".git"
        if git_dir.exists():
            print("✓ Git repository already exists")
            return
        
        # Initialize git repository
        subprocess.run(["git", "init"], cwd=storage_path, check=True, capture_output=True)
        print("✓ Git repository initialized")
        
        # Create initial commit
        readme_path = storage_path / "README.md"
        readme_path.write_text("# NCM Platform Configuration Storage\n\nThis directory stores device configurations versioned with Git.\n")
        
        subprocess.run(["git", "add", "README.md"], cwd=storage_path, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=storage_path, check=True, capture_output=True)
        print("✓ Initial Git commit created")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Error initializing Git repository: {e}")
    except FileNotFoundError:
        print("⚠️  Git not found. Skipping repository initialization.")


def main():
    """Main initialization function"""
    print("=" * 60)
    print("NCM Platform - Database Initialization")
    print("=" * 60)
    
    # Check environment variables
    print(f"\nDatabase URL: {settings.DATABASE_URL}")
    print(f"Git Storage Path: {settings.GIT_REPO_PATH}")
    print()
    
    try:
        # Create storage directories
        create_storage_directories()
        
        # Initialize database
        init_database()
        
        # Create admin user
        create_admin_user()
        
        # Initialize Git repository
        init_git_repository()
        
        print("\n" + "=" * 60)
        print("✓ Initialization completed successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Start Redis: redis-server")
        print("2. Start Celery worker: celery -A app.tasks.celery_app worker --loglevel=info")
        print("3. Start API server: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("4. Access the platform: http://localhost:8000")
        print("5. Login with admin/admin123 and change the password immediately!")
        
    except Exception as e:
        print(f"\n✗ Initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
