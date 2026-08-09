import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_user(db_session: Session):
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("admin"),
        is_active=True,
        is_admin=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(client: TestClient, admin_user: User):
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin"},
    )
    return response.json()["access_token"]


def test_get_settings(client: TestClient, auth_token: str):
    response = client.get(
        "/settings/",
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "db_url" in data
    assert "redis_url" in data
    assert "enable_email" in data


def test_update_settings(client: TestClient, auth_token: str):
    payload = {
        "db_url": "postgresql://test_user:test_password@localhost:5432/test_db",
        "redis_url": "redis://localhost:6379/1",
        "enable_email": True,
        "email_smtp": "smtp.test.com",
        "email_port": "25",
        "session_timeout": "60",
        "max_login_attempts": "3",
        "api_timeout": "15",
        "max_concurrent_backups": "5"
    }
    response = client.put(
        "/settings/",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["db_url"] == payload["db_url"]
    assert data["redis_url"] == payload["redis_url"]
    assert data["enable_email"] is True
    assert data["email_smtp"] == "smtp.test.com"


def test_settings_require_auth(client: TestClient):
    response = client.get("/settings/")
    assert response.status_code == 401
