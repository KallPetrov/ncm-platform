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
    """Create a test database session and clean up after"""
    db = SessionLocal()
    # Clean up previous E2E test data if any
    db.query(User).filter(User.username == "e2e_user").delete()
    db.query(DeviceModel).filter(DeviceModel.name == "E2E Router").delete()
    db.commit()
    try:
        yield db
    finally:
        db.query(User).filter(User.username == "e2e_user").delete()
        db.query(DeviceModel).filter(DeviceModel.name == "E2E Router").delete()
        db.commit()
        db.close()


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


def test_full_platform_e2e_lifecycle(client: TestClient, db_session: Session):
    """
    End-to-End Test covering:
    1. User Registration & Login (JWT Authentication)
    2. Device Provisioning (Secrets Vault secure credentials + Connection test)
    3. Configuration Validation & Manual Command validation
    4. Compliance Audit & Rules Verification
    5. Web SSH session and security tokens
    6. Live Database stats query through AI Assistant
    """
    # ==========================================
    # 1. User Registration & Login
    # ==========================================
    reg_payload = {
        "username": "e2e_user",
        "email": "e2e_user@example.com",
        "password": "e2epassword123",
        "is_admin": True
    }
    reg_response = client.post("/auth/register", json=reg_payload)
    assert reg_response.status_code in (200, 201, 400)

    login_payload = {
        "username": "e2e_user",
        "password": "e2epassword123"
    }
    login_response = client.post("/auth/login", data=login_payload)
    assert login_response.status_code == 200
    auth_data = login_response.json()
    token = auth_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # ==========================================
    # 2. Device Provisioning (Secure Vault integration)
    # ==========================================
    device_payload = {
        "name": "E2E Router",
        "ip_address": "127.0.0.1",
        "device_type": "router",
        "vendor": "Cisco",
        "status": "online",
        "username": "admin",
        "password": "CiscoPassword123!",
        "connection_protocol": "ssh",
        "port": 22
    }
    device_response = client.post("/devices/", json=device_payload, headers=headers)
    assert device_response.status_code in (200, 201)
    device_data = device_response.json()
    device_id = device_data["id"]

    # Verify credentials encryption in Secrets Vault
    db_device = db_session.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    assert db_device is not None
    assert db_device.password != "CiscoPassword123!"  # Must be hashed/encrypted

    # Connection test check
    conn_response = client.post(f"/devices/{device_id}/test-connection", headers=headers)
    assert conn_response.status_code == 200
    conn_data = conn_response.json()
    assert "success" in conn_data
    assert "connected" in conn_data

    # ==========================================
    # 3. Configuration & Command Validation
    # ==========================================
    validation_payload = {
        "device_id": device_id,
        "commands": [
            "interface GigabitEthernet0/1",
            "ip address 10.10.10.1 255.255.255.0",
            "no shutdown"
        ]
    }
    val_response = client.post("/configurations/validate-commands", json=validation_payload, headers=headers)
    assert val_response.status_code == 200
    val_data = val_response.json()
    assert val_data["success"] is True

    # ==========================================
    # 4. Compliance Audit Rules Verification
    # ==========================================
    compliance_response = client.post(f"/configurations/evaluate-compliance/{device_id}", headers=headers)
    assert compliance_response.status_code in (200, 404)

    # Audit trail checking
    audit_response = client.get("/audit-logs/", headers=headers)
    assert audit_response.status_code == 200
    audit_data = audit_response.json()
    assert len(audit_data) > 0
    assert any("e2e_user" in log["username"] for log in audit_data)

    # ==========================================
    # 5. Web SSH session & security tokens
    # ==========================================
    ssh_session_payload = {
        "device_id": device_id
    }
    ssh_response = client.post("/ssh/sessions", json=ssh_session_payload, headers=headers)
    assert ssh_response.status_code in (200, 201)
    ssh_data = ssh_response.json()
    assert ssh_data["status"] in ("active", "pending")
    assert "session_token" in ssh_data

    # ==========================================
    # 6. AI Assistant Queries Integration (Stats & Live info)
    # ==========================================
    ai_suggestions_response = client.get("/ai/suggestions", headers=headers)
    assert ai_suggestions_response.status_code == 200
    suggestions = ai_suggestions_response.json()
    assert len(suggestions) > 0

    ai_chat_payload = {
        "message": "колко устройства имаме общо в платформата и в какъв статус са?"
    }
    ai_chat_response = client.post("/ai/chat", json=ai_chat_payload, headers=headers)
    assert ai_chat_response.status_code == 200
    ai_chat_data = ai_chat_response.json()
    assert "response" in ai_chat_data
    assert any(word in ai_chat_data["response"] for word in ("Router", "устройства", "общо", "офлайн", "онлайн"))
