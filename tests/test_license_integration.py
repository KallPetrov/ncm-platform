import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.license_manager import LicenseManager
from app.models.device import Device
from app.models.user import User
from app.core.database import SessionLocal
from app.core.security import get_password_hash

client = TestClient(app)


@pytest.fixture(autouse=True)
def seed_admin_and_license():
    """Seed the admin user and ensure no license key initially exists."""
    import os
    os.environ["LANI_TEST_LICENSE_ENFORCEMENT"] = "1"
    db = SessionLocal()

    # Create test admin user if not exists
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin"),
            is_active=True,
            is_admin=True
        )
        db.add(admin)
        db.commit()

    # Ensure no license file exists
    path = LicenseManager.get_license_file_path()
    if os.path.exists(path):
        os.remove(path)

    yield db

    # Cleanup
    if os.path.exists(path):
        os.remove(path)
    os.environ.pop("LANI_TEST_LICENSE_ENFORCEMENT", None)
    db.close()


def get_auth_headers():
    """Helper to get JWT auth headers."""
    response = client.post("/auth/login", data={"username": "admin", "password": "admin"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_api_license_status_unlicensed():
    """Verify GET /api/settings/license when no license is installed."""
    headers = get_auth_headers()
    response = client.get("/settings/license", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert data["max_devices"] == 3


def test_api_upload_valid_license():
    """Verify uploading a valid signed license unlocks the platform."""
    headers = get_auth_headers()

    # Generate a valid test key
    valid_key = LicenseManager.generate_signed_license_for_test(
        owner="Тест Клиент",
        expires_at="2027-01-01",
        max_devices=50
    )

    response = client.post("/settings/license", json={"license_key": valid_key}, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["owner"] == "Тест Клиент"
    assert data["max_devices"] == 50


def test_api_upload_invalid_license():
    """Verify uploading an invalid license is rejected with 400."""
    headers = get_auth_headers()
    response = client.post("/settings/license", json={"license_key": "invalid-base64-key-here"}, headers=headers)
    assert response.status_code == 400


def test_ai_blocked_when_unlicensed():
    """Verify that calling AI chat when unlicensed returns 402 Payment Required."""
    headers = get_auth_headers()
    response = client.post("/ai/chat", json={"message": "Здравей"}, headers=headers)
    assert response.status_code == 402
    assert "изисква активен търговски лиценз" in response.json()["detail"]


def test_web_ssh_blocked_when_unlicensed():
    """Verify that starting SSH session when unlicensed returns 402."""
    headers = get_auth_headers()
    response = client.post("/ssh/sessions", json={"device_id": 1}, headers=headers)
    assert response.status_code == 402
    assert "изисква активен търговски лиценз" in response.json()["detail"]


def test_device_limit_enforced():
    """Verify that creating more than 3 devices when unlicensed returns 402."""
    headers = get_auth_headers()
    db = SessionLocal()

    # Clear devices from DB for clean testing environment
    db.query(Device).delete()
    db.commit()

    # Create 3 devices successfully (within Demo limit)
    for i in range(1, 4):
        resp = client.post(
            "/devices/",
            json={
                "name": f"Dev-{i}",
                "ip_address": f"192.168.1.{i}",
                "device_type": "router",
                "vendor": "cisco",
                "model": "2911",
                "location": "Sofia",
                "username": "admin",
                "password": "password123",
                "port": 22
            },
            headers=headers
        )
        assert resp.status_code == 200

    # The 4th device creation must be blocked with 402 Payment Required
    resp = client.post(
        "/devices/",
        json={
            "name": "Dev-4",
            "ip_address": "192.168.1.4",
            "device_type": "router",
            "vendor": "cisco",
            "model": "2911",
            "location": "Sofia",
            "username": "admin",
            "password": "password123",
            "port": 22
        },
        headers=headers
    )
    assert resp.status_code == 402
    assert "Достигнат е лимитът на устройства" in resp.json()["detail"]

    db.close()
