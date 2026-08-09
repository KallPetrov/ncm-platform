import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import SessionLocal
from app.models.device import Device as DeviceModel, Configuration
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
@pytest.mark.automation
class TestAutomationAPI:
    def test_list_predefined_templates(self, client: TestClient, auth_token: str):
        response = client.get(
            "/automation/templates",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert any(item["name"] == "cisco_snmp_config" for item in data)

    def test_validate_template(self, client: TestClient, auth_token: str):
        response = client.post(
            "/automation/validate-template",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"template": "hostname {{ device_name }}\n"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True

    def test_apply_template_to_device(self, client: TestClient, auth_token: str, db_session: Session):
        device = DeviceModel(
            name="Automation Device",
            ip_address="192.168.1.30",
            device_type="router",
            vendor="Cisco",
            status="online",
            username="admin",
            password=get_password_hash("password"),
            connection_protocol="ssh",
            port=22,
        )
        db_session.add(device)
        db_session.commit()
        db_session.refresh(device)

        response = client.post(
            "/automation/apply",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "device_ids": [device.id],
                "template": "hostname {{ device_name }}",
                "variables": {"device_name": "automation-router"},
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_devices"] == 1
        assert isinstance(data["results"], list)


@pytest.mark.unit
@pytest.mark.change_management
class TestChangeManagementAPI:
    def test_analyze_configuration_changes(self, client: TestClient, auth_token: str, db_session: Session):
        device = DeviceModel(
            name="Change Device",
            ip_address="192.168.1.31",
            device_type="router",
            vendor="Cisco",
            status="online",
            username="admin",
            password=get_password_hash("password"),
            connection_protocol="ssh",
            port=22,
        )
        db_session.add(device)
        db_session.commit()
        db_session.refresh(device)

        config1 = Configuration(device_id=device.id, version=1, content="hostname old-router\n")
        config2 = Configuration(device_id=device.id, version=2, content="hostname new-router\n")
        db_session.add_all([config1, config2])
        db_session.commit()

        response = client.get(
            f"/change-management/device/{device.id}/analysis",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["device_id"] == device.id
        assert data["has_changes"] is True
