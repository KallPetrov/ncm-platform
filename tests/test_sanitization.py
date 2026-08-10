import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from app.services.sanitization import SanitizationService


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
        username="admin_sanit",
        email="admin_sanit@example.com",
        hashed_password=get_password_hash("admin"),
        is_active=True,
        is_admin=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def auth_token(client: TestClient, admin_user: User):
    """Get authentication token for admin user"""
    response = client.post(
        "/auth/login",
        data={"username": "admin_sanit", "password": "admin"}
    )
    return response.json()["access_token"]


def test_sanitization_service_passwords():
    """Test standard cisco-style password and secret redaction"""
    raw_config = (
        "hostname TestRouter\n"
        "enable password 7 02070D48074E1E1C\n"
        "enable secret 5 $1$mERr$Odf.P00T7P723Eee7Vp8c/\n"
        "username admin privilege 15 password my_plain_password\n"
        "username test secret 5 $1$mERr$Odf.P\n"
        "password=xyz123\n"
    )

    sanitized = SanitizationService.sanitize_configuration(raw_config)

    assert "02070D48074E1E1C" not in sanitized
    assert "$1$mERr$Odf.P00T7P723Eee7Vp8c/" not in sanitized
    assert "my_plain_password" not in sanitized
    assert "xyz123" not in sanitized

    assert "enable password 7 <REDACTED_PASSWORD>" in sanitized
    assert "enable secret 5 <REDACTED_PASSWORD>" in sanitized
    assert "username admin privilege 15 password <REDACTED_PASSWORD>" in sanitized
    assert "username test secret 5 <REDACTED_PASSWORD>" in sanitized
    assert "password=<REDACTED_PASSWORD>" in sanitized


def test_sanitization_service_psk():
    """Test Pre-Shared Key redaction"""
    raw_config = (
        "crypto isakmp key super-secret-key-123 address 10.1.1.1\n"
        "pre-shared-key 7 045802150C2E\n"
        "wpa-psk ascii wpa_plain_key\n"
    )

    sanitized = SanitizationService.sanitize_configuration(raw_config)

    assert "super-secret-key-123" not in sanitized
    assert "045802150C2E" not in sanitized
    assert "wpa_plain_key" not in sanitized

    assert "crypto isakmp key <REDACTED_KEY> address 10.1.1.1" in sanitized
    assert "pre-shared-key 7 <REDACTED_KEY>" in sanitized
    assert "wpa-psk ascii <REDACTED_KEY>" in sanitized


def test_sanitization_service_snmp():
    """Test SNMP community string redaction"""
    raw_config = (
        "snmp-server community public RO\n"
        "snmp-server community private RW\n"
        "snmp community set default-name name=public-community\n"
    )

    sanitized = SanitizationService.sanitize_configuration(raw_config)

    assert "public" not in sanitized
    assert "private" not in sanitized
    assert "public-community" not in sanitized

    assert "snmp-server community <REDACTED_COMMUNITY> RO" in sanitized
    assert "snmp-server community <REDACTED_COMMUNITY> RW" in sanitized
    assert "snmp community set default-name name=<REDACTED_COMMUNITY>" in sanitized


def test_sanitization_service_private_keys():
    """Test PEM format private key redaction"""
    raw_config = (
        "hostname Switch1\n"
        "-----BEGIN RSA PRIVATE KEY-----\n"
        "MIIEowIBAAKCAQEAzsYV2gR+4uUjR/...\n"
        "7K8D5iN...==\n"
        "-----END RSA PRIVATE KEY-----\n"
        "ip ssh version 2\n"
    )

    sanitized = SanitizationService.sanitize_configuration(raw_config)

    assert "MIIEowIBAAKCAQEAzsYV2gR+4uUjR" not in sanitized
    assert "7K8D5iN" not in sanitized
    assert "-----BEGIN PRIVATE KEY-----\n[REDACTED_PRIVATE_KEY]\n-----END PRIVATE KEY-----" in sanitized


def test_sanitization_api_endpoint(client: TestClient, auth_token: str):
    """Test the /configurations/sanitize API endpoint"""
    raw_config = "enable secret 5 $1$mERr$Odf.P00T7P723Eee7Vp8c/\nsnmp-server community private RW"

    response = client.post(
        "/configurations/sanitize",
        json={"content": raw_config, "device_type": "router"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "sanitized_content" in data
    assert "original_size" in data
    assert "sanitized_size" in data

    sanitized_content = data["sanitized_content"]
    assert "$1$mERr$Odf.P00T7P723Eee7Vp8c/" not in sanitized_content
    assert "private" not in sanitized_content
    assert "enable secret 5 <REDACTED_PASSWORD>" in sanitized_content
    assert "snmp-server community <REDACTED_COMMUNITY> RW" in sanitized_content
