import pytest
import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import SessionLocal
from app.models.device import Device as DeviceModel
from app.models.user import User
from app.models.firmware import FirmwareImage, UpgradeJob
from app.core.security import get_password_hash
from app.services.firmware_upgrade import FirmwareUpgradeService


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
        username="admin_fw",
        email="admin_fw@example.com",
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
    """Create a test device with configuration"""
    device = DeviceModel(
        name="Upgrade Router",
        ip_address="192.168.1.50",
        device_type="router",
        vendor="Cisco",
        status="online",
        username="admin",
        password=get_password_hash("device_password"),
        enable_password=get_password_hash("enable_password"),
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
        data={"username": "admin_fw", "password": "admin"}
    )
    return response.json()["access_token"]


def test_register_and_list_firmware(client: TestClient, auth_token: str):
    """Test registering a firmware image and listing registered images"""
    # Register image
    payload = {
        "filename": "c3900-universalk9-mz.SPA.155-3.M6.bin",
        "version": "15.5(3)M6",
        "device_type": "router",
        "vendor": "Cisco",
        "md5_hash": "2f6e9112999e82c50889d8960e9ed4ab",
        "file_size": 85000000,
        "file_path": "/var/lib/tftpboot/c3900-universalk9-mz.SPA.155-3.M6.bin"
    }

    response = client.post(
        "/firmware/images",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == payload["filename"]
    assert data["version"] == payload["version"]
    assert "id" in data

    # List images
    list_response = client.get(
        "/firmware/images",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert list_response.status_code == 200
    images = list_response.json()
    assert len(images) > 0
    assert any(img["filename"] == payload["filename"] for img in images)


def test_firmware_upgrade_lifecycle(client: TestClient, auth_token: str, test_device: DeviceModel, db_session: Session):
    """Test trigger upgrade and complete lifecycle verify"""
    # Create firmware image
    firmware = FirmwareImage(
        filename="c3900-universalk9-mz.bin",
        version="15.5(3)M6",
        device_type="router",
        vendor="Cisco",
        md5_hash="2f6e9112999e82c50889d8960e9ed4ab",
        file_size=50000000,
        file_path="/var/lib/tftp/c3900-universalk9-mz.bin"
    )
    db_session.add(firmware)
    db_session.commit()
    db_session.refresh(firmware)

    # Trigger upgrade
    payload = {
        "device_id": test_device.id,
        "firmware_image_id": firmware.id
    }

    response = client.post(
        "/firmware/upgrade",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["device_id"] == test_device.id
    assert data["firmware_image_id"] == firmware.id

    pre_checks = json.loads(data["pre_check_results"])
    assert pre_checks["space_verified"] is True
    assert pre_checks["current_version"] == "15.1"

    post_checks = json.loads(data["post_check_results"])
    assert post_checks["upgraded_successfully"] is True
    assert post_checks["active_version"] == firmware.version

    # Get job status
    job_id = data["id"]
    job_response = client.get(
        f"/firmware/jobs/{job_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert job_response.status_code == 200
    job_data = job_response.json()
    assert job_data["status"] == "success"


def test_firmware_upgrade_not_found(client: TestClient, auth_token: str):
    """Test firmware upgrade with invalid device or firmware"""
    # Invalid device
    payload = {
        "device_id": 99999,
        "firmware_image_id": 1
    }
    response = client.post(
        "/firmware/upgrade",
        json=payload,
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404

    # Invalid job status query
    job_response = client.get(
        "/firmware/jobs/99999",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert job_response.status_code == 404
