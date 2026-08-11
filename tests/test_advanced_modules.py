import pytest
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.device import Device, DeviceType, DeviceStatus
from app.services.secrets_vault import SecretsVaultService
from app.services.ssot_sync import SSOTSyncService
from app.services.topology import TopologyService
from app.services.ai_analysis import AIAnalysisService


@pytest.fixture
def db_session():
    """Create a test database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_device(db_session: Session):
    """Create a test device for advanced operations"""
    device = Device(
        name="Router-X",
        ip_address="192.168.99.1",
        device_type="router",
        vendor="Cisco",
        status="online",
        username="admin",
        password="my_password",
        connection_protocol="ssh",
        port=22
    )
    db_session.add(device)
    db_session.commit()
    db_session.refresh(device)
    return device


def test_secrets_vault_encryption():
    """Test encryption and decryption roundtrip"""
    plaintext = "super-secret-password-123"
    encrypted = SecretsVaultService.encrypt_secret(plaintext)
    assert encrypted != plaintext

    decrypted = SecretsVaultService.decrypt_secret(encrypted)
    assert decrypted == plaintext


def test_secrets_vault_rotation(db_session: Session, test_device: Device):
    """Test automated password rotation and database update"""
    res = SecretsVaultService.rotate_device_password(db_session, test_device.id, "new_secure_pass_456", is_testing=True)
    assert res["success"] is True

    # Reload from DB and verify encrypted password can be decrypted
    db_session.refresh(test_device)
    decrypted = SecretsVaultService.decrypt_secret(test_device.password)
    assert decrypted == "new_secure_pass_456"


def test_ssot_sync_import(db_session: Session):
    """Test NetBox inventory sync import workflow"""
    res = SSOTSyncService.sync_devices_from_netbox(db_session, "http://netbox.local", "dummy_token", is_testing=True)
    assert res["success"] is True
    assert res["added_count"] > 0

    # Verify devices are in DB
    nb_device = db_session.query(Device).filter(Device.name == "NetBox-Router-1").first()
    assert nb_device is not None
    assert nb_device.ip_address == "192.168.10.1"


def test_ssot_sync_push(db_session: Session, test_device: Device):
    """Test pushing status back to NetBox"""
    res = SSOTSyncService.push_local_changes_to_netbox(db_session, test_device.id, "http://netbox.local", "token", is_testing=True)
    assert res["success"] is True


def test_topology_neighbors_discovery(db_session: Session, test_device: Device):
    """Test CDP neighbor parsing and topology construction"""
    # Create another device
    device2 = Device(
        name="Switch-P",
        ip_address="192.168.99.2",
        device_type="switch",
        vendor="Cisco",
        status="online",
        username="admin",
        password="password",
        connection_protocol="ssh",
        port=22
    )
    db_session.add(device2)
    db_session.commit()

    edges = TopologyService.discover_topology_edges(db_session, is_testing=True)
    assert len(edges) > 0
    assert "source_name" in edges[0]
    assert "target_name" in edges[0]


def test_ai_diff_explanation():
    """Test translating unified diff to plain Bulgarian language"""
    diff_sample = (
        "--- old_config\n"
        "+++ new_config\n"
        "- shutdown\n"
        "+ no shutdown\n"
        "+ transport input telnet\n"
        "+ access-list 101 permit ip any any\n"
    )
    explanation = AIAnalysisService.explain_configuration_diff_ai(diff_sample)

    assert "no shutdown" in diff_sample
    assert "Telnet" in explanation
    assert "permit any" in explanation


def test_ai_anomaly_detection():
    """Test scanning configuration content for anomalies"""
    config_sample = (
        "hostname BorderRouter\n"
        "snmp-server community public RO\n"
        "line vty 0 4\n"
        " transport input telnet\n"
    )
    anomalies = AIAnalysisService.detect_configuration_anomalies(config_sample)

    assert len(anomalies) > 0
    categories = [a["category"] for a in anomalies]
    assert "security" in categories
    assert "access_control" in categories
