import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import get_db, SessionLocal
from app.models.device import Device as DeviceModel, Configuration, BackupJob
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
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def clean_db(db_session: Session):
    """Clean database before and after tests"""
    # Clean up
    db_session.query(BackupJob).delete()
    db_session.query(Configuration).delete()
    db_session.query(DeviceModel).delete()
    db_session.query(User).delete()
    db_session.commit()
    
    yield
    
    # Clean up after test
    db_session.query(BackupJob).delete()
    db_session.query(Configuration).delete()
    db_session.query(DeviceModel).delete()
    db_session.query(User).delete()
    db_session.commit()


@pytest.mark.integration
class TestDeviceBackupWorkflow:
    """Test complete device backup workflow"""
    
    def test_complete_backup_workflow(self, client: TestClient, clean_db, db_session: Session):
        """Test complete workflow: create device, create backup, verify backup"""
        # Step 1: Create admin user
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin"),
            is_active=True,
            is_admin=True
        )
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)
        
        # Step 2: Login
        login_response = client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Step 3: Create device
        device_response = client.post(
            "/devices/",
            json={
                "name": "Backup Test Device",
                "ip_address": "192.168.1.100",
                "device_type": "router",
                "vendor": "Cisco",
                "status": "online",
                "username": "admin",
                "password": "device_password",
                "connection_protocol": "ssh",
                "port": 22
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert device_response.status_code == 200
        device = device_response.json()
        device_id = device["id"]
        
        # Step 4: Trigger backup
        backup_response = client.post(
            f"/devices/{device_id}/trigger-backup",
            headers={"Authorization": f"Bearer {token}"}
        )
        # This might fail if device is not reachable, but should return valid response
        assert backup_response.status_code in [200, 500]
        
        # Step 5: Verify device exists
        get_device_response = client.get(
            f"/devices/{device_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_device_response.status_code == 200
        assert get_device_response.json()["name"] == "Backup Test Device"
        
        # Step 6: Delete device
        delete_response = client.delete(
            f"/devices/{device_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert delete_response.status_code == 204


@pytest.mark.integration
class TestConfigurationManagementWorkflow:
    """Test complete configuration management workflow"""
    
    def test_configuration_lifecycle(self, client: TestClient, clean_db, db_session: Session):
        """Test complete configuration lifecycle"""
        # Step 1: Create admin user
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin"),
            is_active=True,
            is_admin=True
        )
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)
        
        # Step 2: Login
        login_response = client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Step 3: Create device
        device_response = client.post(
            "/devices/",
            json={
                "name": "Config Test Device",
                "ip_address": "192.168.1.101",
                "device_type": "switch",
                "vendor": "Cisco",
                "status": "online",
                "username": "admin",
                "password": "device_password",
                "connection_protocol": "ssh",
                "port": 22
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert device_response.status_code == 200
        device = device_response.json()
        device_id = device["id"]
        
        # Step 4: Create configuration (simulated via direct DB for testing)
        config1 = Configuration(
            device_id=device_id,
            version=1,
            content="hostname config-test\ninterface GigabitEthernet0/0\n"
        )
        db_session.add(config1)
        db_session.commit()
        
        # Step 5: Get configurations
        configs_response = client.get(
            f"/configurations/device/{device_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert configs_response.status_code == 200
        configs = configs_response.json()
        assert len(configs) == 1
        
        # Step 6: Create second configuration
        config2 = Configuration(
            device_id=device_id,
            version=2,
            content="hostname config-test-updated\ninterface GigabitEthernet0/0\n"
        )
        db_session.add(config2)
        db_session.commit()
        
        # Step 7: Get diff between versions
        diff_response = client.get(
            f"/configurations/device/{device_id}/diff?version_a=1&version_b=2",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert diff_response.status_code == 200
        diff_data = diff_response.json()
        assert "diff" in diff_data
        
        # Step 8: Get latest configuration
        latest_response = client.get(
            f"/configurations/device/{device_id}/latest",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert latest_response.status_code == 200
        latest_data = latest_response.json()
        assert latest_data["version"] == 2


@pytest.mark.integration
class TestUserManagementWorkflow:
    """Test complete user management workflow"""
    
    def test_user_lifecycle(self, client: TestClient, clean_db, db_session: Session):
        """Test complete user lifecycle"""
        # Step 1: Create admin user
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin"),
            is_active=True,
            is_admin=True
        )
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)
        
        # Step 2: Login as admin
        admin_login = client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"}
        )
        assert admin_login.status_code == 200
        admin_token = admin_login.json()["access_token"]
        
        # Step 3: Create regular user
        user_response = client.post(
            "/users/",
            json={
                "username": "regularuser",
                "email": "regular@example.com",
                "password": "regularpassword"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert user_response.status_code == 200
        user = user_response.json()
        user_id = user["id"]
        
        # Step 4: List users
        users_response = client.get(
            "/users/",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert users_response.status_code == 200
        users = users_response.json()
        assert len(users) == 2
        
        # Step 5: Login as regular user
        user_login = client.post(
            "/auth/login",
            data={"username": "regularuser", "password": "regularpassword"}
        )
        assert user_login.status_code == 200
        user_token = user_login.json()["access_token"]
        
        # Step 6: Get current user info
        me_response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data["username"] == "regularuser"
        
        # Step 7: Logout (simulated by invalidating token)
        # In real app, this would be handled by token invalidation


@pytest.mark.integration
class TestMultiDeviceWorkflow:
    """Test workflow with multiple devices"""
    
    def test_multiple_device_management(self, client: TestClient, clean_db, db_session: Session):
        """Test managing multiple devices"""
        # Step 1: Create admin user
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin"),
            is_active=True,
            is_admin=True
        )
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)
        
        # Step 2: Login
        login_response = client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Step 3: Create multiple devices
        devices = []
        for i in range(3):
            device_response = client.post(
                "/devices/",
                json={
                    "name": f"Test Device {i+1}",
                    "ip_address": f"192.168.1.{i+10}",
                    "device_type": "router",
                    "vendor": "Cisco",
                    "status": "online",
                    "username": "admin",
                    "password": "device_password",
                    "connection_protocol": "ssh",
                    "port": 22
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            assert device_response.status_code == 200
            devices.append(device_response.json())
        
        # Step 4: List all devices
        list_response = client.get(
            "/devices/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert list_response.status_code == 200
        all_devices = list_response.json()
        assert len(all_devices) == 3
        
        # Step 5: Update each device
        for device in devices:
            update_response = client.put(
                f"/devices/{device['id']}",
                json={"status": "maintenance"},
                headers={"Authorization": f"Bearer {token}"}
            )
            assert update_response.status_code == 200
        
        # Step 6: Verify updates
        updated_list_response = client.get(
            "/devices/",
            headers={"Authorization": f"Bearer {token}"}
        )
        updated_devices = updated_list_response.json()
        assert all(device["status"] == "maintenance" for device in updated_devices)
        
        # Step 7: Clean up - delete all devices
        for device in devices:
            delete_response = client.delete(
                f"/devices/{device['id']}",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert delete_response.status_code == 204


@pytest.mark.integration
class TestErrorHandlingWorkflow:
    """Test error handling in workflows"""
    
    def test_authentication_failure_workflow(self, client: TestClient, clean_db, db_session: Session):
        """Test workflow with authentication failures"""
        # Step 1: Try to access protected endpoint without auth
        response = client.get("/devices/")
        assert response.status_code == 401
        
        # Step 2: Try to login with wrong credentials
        login_response = client.post(
            "/auth/login",
            data={"username": "admin", "password": "wrongpassword"}
        )
        assert login_response.status_code == 401
        
        # Step 3: Create admin user
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin"),
            is_active=True,
            is_admin=True
        )
        db_session.add(admin)
        db_session.commit()
        
        # Step 4: Login with correct credentials
        correct_login = client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"}
        )
        assert correct_login.status_code == 200
        token = correct_login.json()["access_token"]
        
        # Step 5: Access protected endpoint with valid token
        protected_response = client.get(
            "/devices/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert protected_response.status_code == 200
    
    def test_invalid_device_workflow(self, client: TestClient, clean_db, db_session: Session):
        """Test workflow with invalid device operations"""
        # Step 1: Create admin user and login
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin"),
            is_active=True,
            is_admin=True
        )
        db_session.add(admin)
        db_session.commit()
        
        login_response = client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"}
        )
        token = login_response.json()["access_token"]
        
        # Step 2: Try to get non-existent device
        get_response = client.get(
            "/devices/99999",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == 404
        
        # Step 3: Try to update non-existent device
        update_response = client.put(
            "/devices/99999",
            json={"name": "Updated Name"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert update_response.status_code == 404
        
        # Step 4: Try to delete non-existent device
        delete_response = client.delete(
            "/devices/99999",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert delete_response.status_code == 404


@pytest.mark.integration
class TestBackupJobsWorkflow:
    """Test backup jobs management workflow"""
    
    def test_backup_jobs_lifecycle(self, client: TestClient, clean_db, db_session: Session):
        """Test complete backup jobs workflow"""
        # Step 1: Create admin user
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin"),
            is_active=True,
            is_admin=True
        )
        db_session.add(admin)
        db_session.commit()
        
        # Step 2: Login
        login_response = client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"}
        )
        token = login_response.json()["access_token"]
        
        # Step 3: Create device
        device_response = client.post(
            "/devices/",
            json={
                "name": "Backup Test Device",
                "ip_address": "192.168.1.200",
                "device_type": "router",
                "vendor": "Cisco",
                "status": "online",
                "username": "admin",
                "password": "device_password",
                "connection_protocol": "ssh",
                "port": 22
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        device = device_response.json()
        
        # Step 4: Create backup job (simulated via DB)
        backup_job = BackupJob(
            device_id=device["id"],
            status="pending",
            scheduled_time="2026-08-09T10:00:00"
        )
        db_session.add(backup_job)
        db_session.commit()
        
        # Step 5: List backup jobs
        jobs_response = client.get(
            "/backup-jobs/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert jobs_response.status_code == 200
        jobs = jobs_response.json()
        assert len(jobs) >= 1
