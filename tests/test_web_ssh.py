import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import SessionLocal
from app.models.device import Device as DeviceModel
from app.models.user import User
from app.models.web_ssh import SSHSession, KeystrokeLog
from app.core.security import get_password_hash


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
        username="admin_ssh",
        email="admin_ssh@example.com",
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
    """Create a test device for terminal connection"""
    device = DeviceModel(
        name="SSH Switch",
        ip_address="192.168.1.100",
        device_type="switch",
        vendor="Cisco",
        status="online",
        username="admin",
        password=get_password_hash("device_password"),
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
        data={"username": "admin_ssh", "password": "admin"}
    )
    return response.json()["access_token"]


def test_web_ssh_session_lifecycle(client: TestClient, auth_token: str, test_device: DeviceModel, db_session: Session):
    """Test full lifecycle of a Web SSH session and recorded command logs"""
    # 1. Create a secure SSH session token
    response = client.post(
        "/ssh/sessions",
        json={"device_id": test_device.id},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "active"
    assert "session_token" in data
    assert data["device_id"] == test_device.id

    session_token = data["session_token"]
    session_id = data["id"]

    # 2. Execute a command in terminal session
    exec_response = client.post(
        "/ssh/execute",
        json={"session_token": session_token, "command": "show ip interface brief"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert exec_response.status_code == 200
    exec_data = exec_response.json()
    assert exec_data["success"] is True
    assert exec_data["command"] == "show ip interface brief"
    assert "output" in exec_data

    # 3. View recorded keystroke/command history (Auditor check)
    logs_response = client.get(
        f"/ssh/sessions/{session_id}/logs",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert logs_response.status_code == 200
    logs = logs_response.json()
    assert len(logs) > 0
    assert logs[0]["typed_command"] == "show ip interface brief"

    # 4. Close session
    close_response = client.post(
        "/ssh/close",
        json={"session_token": session_token},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert close_response.status_code == 200
    assert close_response.json()["success"] is True

    # 5. Attempt command execution on closed session
    fail_response = client.post(
        "/ssh/execute",
        json={"session_token": session_token, "command": "show version"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert fail_response.status_code == 400
