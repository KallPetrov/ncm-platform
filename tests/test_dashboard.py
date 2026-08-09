import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import SessionLocal
from app.models.device import Device as DeviceModel, Configuration, BackupJob
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
def client():
    return TestClient(app)


@pytest.fixture
def auth_token(client: TestClient, admin_user: User):
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin"},
    )
    return response.json()["access_token"]


@pytest.mark.unit
@pytest.mark.dashboard
class TestDashboardOverview:
    def test_get_dashboard_overview(self, client: TestClient, auth_token: str, db_session: Session):
        device = DeviceModel(
            name="Overview Device",
            ip_address="192.168.1.20",
            device_type="router",
            vendor="Cisco",
            status="online",
            username="admin",
            password=get_password_hash("device_password"),
            connection_protocol="ssh",
            port=22,
        )
        db_session.add(device)
        db_session.commit()
        db_session.refresh(device)

        config = Configuration(
            device_id=device.id,
            version=1,
            content="hostname overview-router\nservice password-encryption\n",
        )
        db_session.add(config)
        db_session.commit()

        backup_job = BackupJob(
            device_id=device.id,
            status="success",
            scheduled_time="2026-08-09T00:00:00",
        )
        db_session.add(backup_job)
        db_session.commit()

        response = client.get(
            "/dashboard/overview",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_devices"] == 1
        assert data["online_devices"] == 1
        assert data["total_configurations"] == 1
        assert data["successful_backup_jobs"] == 1
        assert data["compliance_summary"]["overall_status"] in {"compliant", "warning", "non_compliant", "error"}
