import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import get_db, SessionLocal
from app.models.device import Device as DeviceModel, Configuration
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
    """Create a test device with configuration"""
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
    
    # Add configuration
    config = Configuration(
        device_id=device.id,
        version=1,
        content="hostname test-router\ninterface GigabitEthernet0/0\n ip address 192.168.1.1 255.255.255.0\n"
    )
    db_session.add(config)
    db_session.commit()
    db_session.refresh(config)
    
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
@pytest.mark.configurations
class TestConfigurationManagement:
    """Test configuration management API endpoints"""
    
    def test_get_device_configurations(self, client: TestClient, auth_token: str, test_device: DeviceModel):
        """Test getting all configurations for a device"""
        response = client.get(
            f"/configurations/device/{test_device.id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]["device_id"] == test_device.id
    
    def test_get_device_configurations_not_found(self, client: TestClient, auth_token: str):
        """Test getting configurations for non-existent device"""
        response = client.get(
            "/configurations/device/99999",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404
    
    def test_get_configuration_by_version(self, client: TestClient, auth_token: str, test_device: DeviceModel):
        """Test getting a specific configuration version"""
        response = client.get(
            f"/configurations/device/{test_device.id}/version/1",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == 1
        assert data["device_id"] == test_device.id
        assert "content" in data
    
    def test_get_configuration_by_version_not_found(self, client: TestClient, auth_token: str, test_device: DeviceModel):
        """Test getting non-existent configuration version"""
        response = client.get(
            f"/configurations/device/{test_device.id}/version/999",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404
    
    def test_get_latest_configuration(self, client: TestClient, auth_token: str, test_device: DeviceModel):
        """Test getting the latest configuration for a device"""
        response = client.get(
            f"/configurations/device/{test_device.id}/latest",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == 1
        assert data["device_id"] == test_device.id
        assert "content" in data
    
    def test_delete_configuration(self, client: TestClient, auth_token: str, db_session: Session):
        """Test deleting a specific configuration"""
        # Create a test configuration
        device = DeviceModel(
            name="Test Device",
            ip_address="192.168.1.2",
            device_type="router",
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
        
        config = Configuration(
            device_id=device.id,
            version=1,
            content="test configuration"
        )
        db_session.add(config)
        db_session.commit()
        db_session.refresh(config)
        
        # Delete the configuration
        response = client.delete(
            f"/configurations/{config.id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 204
    
    def test_delete_configuration_not_found(self, client: TestClient, auth_token: str):
        """Test deleting non-existent configuration"""
        response = client.delete(
            "/configurations/99999",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404
    
    def test_delete_all_device_configurations(self, client: TestClient, auth_token: str, db_session: Session):
        """Test deleting all configurations for a device"""
        # Create a test device with configurations
        device = DeviceModel(
            name="Test Device",
            ip_address="192.168.1.3",
            device_type="router",
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
        
        config1 = Configuration(
            device_id=device.id,
            version=1,
            content="test configuration 1"
        )
        config2 = Configuration(
            device_id=device.id,
            version=2,
            content="test configuration 2"
        )
        db_session.add_all([config1, config2])
        db_session.commit()
        
        # Delete all configurations
        response = client.delete(
            f"/configurations/device/{device.id}/all",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 204


@pytest.mark.unit
@pytest.mark.configurations
class TestConfigurationDiff:
    """Test configuration diff functionality"""
    
    def test_configuration_diff(self, client: TestClient, auth_token: str, db_session: Session):
        """Test getting diff between two configuration versions"""
        # Create a test device with multiple configurations
        device = DeviceModel(
            name="Test Device",
            ip_address="192.168.1.4",
            device_type="router",
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
        
        config1 = Configuration(
            device_id=device.id,
            version=1,
            content="hostname old-router\ninterface GigabitEthernet0/0\n ip address 192.168.1.1 255.255.255.0\n"
        )
        config2 = Configuration(
            device_id=device.id,
            version=2,
            content="hostname new-router\ninterface GigabitEthernet0/0\n ip address 192.168.1.1 255.255.255.0\n"
        )
        db_session.add_all([config1, config2])
        db_session.commit()
        
        # Get diff
        response = client.get(
            f"/configurations/device/{device.id}/diff?version_a=1&version_b=2",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "diff" in data
    
    def test_configuration_diff_same_version(self, client: TestClient, auth_token: str, test_device: DeviceModel):
        """Test getting diff between same version"""
        response = client.get(
            f"/configurations/device/{test_device.id}/diff?version_a=1&version_b=1",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "diff" in data


@pytest.mark.unit
@pytest.mark.configurations
class TestConfigurationChanges:
    """Test configuration change detection"""
    
    def test_configuration_changes(self, client: TestClient, auth_token: str, db_session: Session):
        """Test getting configuration changes for a device"""
        # Create a test device with multiple configurations
        device = DeviceModel(
            name="Test Device",
            ip_address="192.168.1.5",
            device_type="router",
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
        
        config1 = Configuration(
            device_id=device.id,
            version=1,
            content="hostname old-router\n"
        )
        config2 = Configuration(
            device_id=device.id,
            version=2,
            content="hostname new-router\n"
        )
        db_session.add_all([config1, config2])
        db_session.commit()
        
        # Get changes
        response = client.get(
            f"/configurations/device/{device.id}/changes",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.unit
@pytest.mark.configurations
class TestConfigurationCompliance:
    """Test compliance evaluation for configurations"""

    def test_get_configuration_compliance(self, client: TestClient, auth_token: str, db_session: Session):
        """Test running compliance checks on a device configuration"""
        device = DeviceModel(
            name="Compliance Device",
            ip_address="192.168.1.7",
            device_type="router",
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

        config = Configuration(
            device_id=device.id,
            version=1,
            content="hostname compliance-router\nservice password-encryption\nip ssh version 2\nlogging 192.0.2.10\nbanner motd ^Unauthorized access^\n"
        )
        db_session.add(config)
        db_session.commit()

        response = client.get(
            f"/configurations/device/{device.id}/compliance",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["device_id"] == device.id
        assert data["overall_status"] in {"compliant", "warning", "non_compliant", "error"}
        assert data["total_rules"] > 0


@pytest.mark.unit
@pytest.mark.configurations
class TestConfigurationAuthentication:
    """Test configuration authentication requirements"""
    
    def test_unauthorized_access(self, client: TestClient):
        """Test accessing configuration endpoints without authentication"""
        response = client.get("/configurations/device/1")
        assert response.status_code == 401
    
    def test_get_configurations_without_auth(self, client: TestClient):
        """Test getting configurations without authentication"""
        response = client.get("/configurations/device/1")
        assert response.status_code == 401


@pytest.mark.unit
@pytest.mark.configurations
class TestConfigurationValidation:
    """Test configuration data validation"""
    
    def test_empty_configuration_content(self, client: TestClient, auth_token: str, db_session: Session):
        """Test creating configuration with empty content"""
        device = DeviceModel(
            name="Test Device",
            ip_address="192.168.1.6",
            device_type="router",
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
        
        config = Configuration(
            device_id=device.id,
            version=1,
            content=""
        )
        db_session.add(config)
        db_session.commit()
        
        # Try to get the configuration
        response = client.get(
            f"/configurations/device/{device.id}/version/1",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Should return the configuration even if empty
        assert response.status_code == 200
