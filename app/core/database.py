import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL
is_postgresql_url = DATABASE_URL.startswith("postgres") or DATABASE_URL.startswith("postgresql")


def _is_testing_environment() -> bool:
    return (
        os.getenv("TESTING") == "1"
        or os.getenv("PYTEST_CURRENT_TEST") is not None
        or os.getenv("PYTEST_VERSION") is not None
        or "pytest" in sys.modules
        or any("pytest" in arg for arg in sys.argv)
    )


if _is_testing_environment() or not is_postgresql_url or DATABASE_URL.startswith("sqlite"):
    DATABASE_URL = "sqlite:///./test.db"
else:
    try:
        import psycopg2  # noqa: F401
    except Exception:
        DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db():
    from app.models import user, device  # noqa: F401
    if _is_testing_environment():
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def pytest_runtest_setup(item):
    if _is_testing_environment():
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)


init_db()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
