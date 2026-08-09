import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import get_db, SessionLocal
from app.models.device import Device as DeviceModel
from app.models.user import User
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
        username="admin",
        email="admin@example.com",
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
    """Create a test device"""
    device = DeviceModel(
        name="Test Router",
        ip_address="192.168.1.1",
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
        data={"username": "admin", "password": "admin"}
    )
    return response.json()["access_token"]


@pytest.mark.unit
@pytest.mark.devices
class TestDeviceManagement:
    """Test device management API endpoints"""
    
    def test_create_device(self, client: TestClient, auth_token: str):
        """Test creating a new device"""
        response = client.post(
            "/devices/",
            json={
                "name": "New Switch",
                "ip_address": "192.168.1.2",
                "device_type": "switch",
                "vendor": "Cisco",
                "status": "online",
                "username": "admin",
                "password": "password123",
                "connection_protocol": "ssh",
                "port": 22
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Switch"
        assert data["ip_address"] == "192.168.1.2"
        assert data["device_type"] == "switch"
        assert "id" in data
    
    def test_create_device_missing_fields(self, client: TestClient, auth_token: str):
        """Test creating device with missing required fields"""
        response = client.post(
            "/devices/",
            json={
                "name": "Incomplete Device"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 422
    
    def test_list_devices(self, client: TestClient, auth_token: str, test_device: DeviceModel):
        """Test listing all devices"""
        response = client.get(
            "/devices/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert any(device["name"] == "Test Router" for device in data)
    
    def test_get_device(self, client: TestClient, auth_token: str, test_device: DeviceModel):
        """Test getting a specific device"""
        response = client.get(
            f"/devices/{test_device.id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_device.id
        assert data["name"] == "Test Router"
        assert data["ip_address"] == "192.168.1.1"
    
    def test_get_device_not_found(self, client: TestClient, auth_token: str):
        """Test getting a non-existent device"""
        response = client.get(
            "/devices/99999",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404
    
    def test_update_device(self, client: TestClient, auth_token: str, test_device: DeviceModel):
        """Test updating a device"""
        response = client.put(
            f"/devices/{test_device.id}",
            json={
                "name": "Updated Router",
                "status": "offline"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Router"
        assert data["status"] == "offline"
    
    def test_update_device_not_found(self, client: TestClient, auth_token: str):
        """Test updating a non-existent device"""
        response = client.put(
            "/devices/99999",
            json={"name": "Updated Name"},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404
    
    def test_delete_device(self, client: TestClient, auth_token: str, test_device: DeviceModel):
        """Test deleting a device"""
        response = client.delete(
            f"/devices/{test_device.id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 204
    
    def test_delete_device_not_found(self, client: TestClient, auth_token: str):
        """Test deleting a non-existent device"""
        response = client.delete(
            "/devices/99999",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404


@pytest.mark.unit
@pytest.mark.devices
class TestDeviceConnection:
    """Test device connection testing endpoints"""
    
    def test_device_connection(self, client: TestClient, auth_token: str, test_device: DeviceModel):
        """Test device connection check"""
        response = client.post(
            f"/devices/{test_device.id}/test-connection",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # This might fail if device is not actually reachable
        # but should return a valid response
        assert response.status_code in [200, 500]
        data = response.json()
        assert "connected" in data or "error" in data
    
    def test_trigger_backup(self, client: TestClient, auth_token: str, test_device: DeviceModel):
        """Test triggering backup for a device"""
        response = client.post(
            f"/devices/{test_device.id}/trigger-backup",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # This might fail if device is not actually reachable
        # but should return a valid response
        assert response.status_code in [200, 500]
        data = response.json()
        assert "job_id" in data or "error" in data


@pytest.mark.unit
@pytest.mark.devices
class TestDeviceValidation:
    """Test device data validation"""
    
    def test_invalid_ip_address(self, client: TestClient, auth_token: str):
        """Test creating device with invalid IP address"""
        response = client.post(
            "/devices/",
            json={
                "name": "Invalid IP Device",
                "ip_address": "invalid_ip",
                "device_type": "router",
                "vendor": "Cisco",
                "status": "online",
                "username": "admin",
                "password": "password123",
                "connection_protocol": "ssh",
                "port": 22
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 422
    
    def test_invalid_device_type(self, client: TestClient, auth_token: str):
        """Test creating device with invalid device type"""
        response = client.post(
            "/devices/",
            json={
                "name": "Invalid Type Device",
                "ip_address": "192.168.1.3",
                "device_type": "invalid_type",
                "vendor": "Cisco",
                "status": "online",
                "username": "admin",
                "password": "password123",
                "connection_protocol": "ssh",
                "port": 22
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 422
    
    def test_invalid_port(self, client: TestClient, auth_token: str):
        """Test creating device with invalid port"""
        response = client.post(
            "/devices/",
            json={
                "name": "Invalid Port Device",
                "ip_address": "192.168.1.4",
                "device_type": "router",
                "vendor": "Cisco",
                "status": "online",
                "username": "admin",
                "password": "password123",
                "connection_protocol": "ssh",
                "port": 99999
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 422


@pytest.mark.unit
@pytest.mark.devices
class TestDeviceAuthentication:
    """Test device authentication requirements"""
    
    def test_unauthorized_access(self, client: TestClient):
        """Test accessing device endpoints without authentication"""
        response = client.get("/devices/")
        assert response.status_code == 401
    
    def test_create_device_without_auth(self, client: TestClient):
        """Test creating device without authentication"""
        response = client.post(
            "/devices/",
            json={
                "name": "Unauthorized Device",
                "ip_address": "192.168.1.5",
                "device_type": "router",
                "vendor": "Cisco",
                "status": "online",
                "username": "admin",
                "password": "password123",
                "connection_protocol": "ssh",
                "port": 22
            }
        )
        assert response.status_code == 401
