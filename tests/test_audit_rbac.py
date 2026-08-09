import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import SessionLocal
from app.models.device import Device as DeviceModel
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
def operator_user(db_session: Session):
    user = User(
        username="operator",
        email="operator@example.com",
        hashed_password=get_password_hash("operator"),
        is_active=True,
        is_admin=False,
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


@pytest.fixture
def operator_token(client: TestClient, operator_user: User):
    response = client.post(
        "/auth/login",
        data={"username": "operator", "password": "operator"},
    )
    return response.json()["access_token"]


@pytest.mark.unit
class TestAuditAndRBAC:
    def test_admin_can_list_audit_logs(self, client: TestClient, auth_token: str):
        response = client.get(
            "/audit-logs/",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200

    def test_operator_cannot_list_audit_logs(self, client: TestClient, operator_token: str):
        response = client.get(
            "/audit-logs/",
            headers={"Authorization": f"Bearer {operator_token}"},
        )
        assert response.status_code == 403

    def test_device_creation_is_logged(self, client: TestClient, auth_token: str, db_session: Session):
        response = client.post(
            "/devices/",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "name": "Audit Device",
                "ip_address": "192.168.1.100",
                "device_type": "router",
                "vendor": "Cisco",
                "model": "ISR",
                "connection_protocol": "ssh",
                "port": 22,
                "username": "admin",
                "password": "secret",
                "status": "online",
            },
        )
        assert response.status_code == 200
        device = db_session.query(DeviceModel).filter(DeviceModel.name == "Audit Device").first()
        assert device is not None

    def test_audit_logs_can_be_filtered(self, client: TestClient, auth_token: str):
        response = client.get(
            "/audit-logs/?action=device_created&username=admin&limit=20",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        payload = response.json()
        assert all(item["action"] == "device_created" for item in payload)
        assert all(item["username"] == "admin" for item in payload)

    def test_audit_logs_include_actor_role(self, client: TestClient, auth_token: str):
        response = client.get(
            "/audit-logs/?limit=20",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        payload = response.json()
        assert any(item.get("role") == "admin" for item in payload)
