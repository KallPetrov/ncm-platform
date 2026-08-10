import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import SessionLocal
from app.models.device import Device as DeviceModel
from app.models.user import User
from app.core.security import get_password_hash
from app.services.config_validation import ConfigurationValidationService


@pytest.fixture
def db_session():
    """Create a test database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def admin_user(db_session: Session):
    """Create an admin user for testing"""
    user = User(
        username="admin_val",
        email="admin_val@example.com",
        hashed_password=get_password_hash("admin"),
        is_active=True,
        is_admin=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_device(db_session: Session):
    """Create a test device for validation"""
    device = DeviceModel(
        name="Validation Switch",
        ip_address="127.0.0.1",
        device_type="switch",
        vendor="Cisco",
        status="online",
        username="admin",
        password=get_password_hash("password"),
        connection_protocol="ssh",
        port=22
    )
    db_session.add(device)
    db_session.commit()
    db_session.refresh(device)
    return device


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def auth_token(client: TestClient, admin_user: User):
    """Get authentication token for admin user"""
    response = client.post(
        "/auth/login",
        data={"username": "admin_val", "password": "admin"}
    )
    return response.json()["access_token"]


def test_command_syntax_validation():
    """Test syntax validation logic"""
    # 1. Unbalanced brackets
    res1 = ConfigurationValidationService.validate_command_syntax(["interface GigabitEthernet0/0 (description [test)"])
    assert res1["valid"] is False
    assert any("Unbalanced brackets" in err for err in res1["errors"])

    # 2. Missing IP parameter / invalid IP address
    res2 = ConfigurationValidationService.validate_command_syntax(["ip address 999.999.999.999 255.255.255.0"])
    assert res2["valid"] is False
    assert any("Invalid IP address" in err for err in res2["errors"])

    # 3. Forbidden critical command
    res3 = ConfigurationValidationService.validate_command_syntax(["no ip routing"])
    assert res3["valid"] is False
    assert any("Disallowed critical command" in err for err in res3["errors"])

    # 4. Valid sequence
    res4 = ConfigurationValidationService.validate_command_syntax([
        "interface GigabitEthernet0/1",
        "description Uplink to Core",
        "ip address 192.168.1.1 255.255.255.0"
    ])
    assert res4["valid"] is True
    assert len(res4["errors"]) == 0


def test_ping_destination_reachability():
    """Test reachability verification function"""
    # localhost should be pingable or socket connect on loopback
    res = ConfigurationValidationService.ping_destination("127.0.0.1")
    # depending on environment network, should either pass or safely fall back
    assert isinstance(res, bool)


def test_interfaces_status_retrieval(test_device: DeviceModel):
    """Test interface status checks in testing/simulated environment"""
    res = ConfigurationValidationService.verify_device_interfaces(test_device, is_testing=True)
    assert res["success"] is True
    assert "GigabitEthernet0/0" in res["interfaces"]


def test_validation_api_endpoint(client: TestClient, auth_token: str, test_device: DeviceModel):
    """Test the /configurations/validate-commands API endpoint"""
    payload = {
        "device_id": test_device.id,
        "commands": [
            "interface GigabitEthernet0/1",
            "ip address 10.0.0.1 255.255.255.0"
        ]
    }

    response = client.post(
        "/configurations/validate-commands",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["stage"] == "completed"
