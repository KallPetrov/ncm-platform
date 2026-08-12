import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.database import SessionLocal
from app.models.device import Device as DeviceModel, DeviceStatus, Configuration
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
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def test_admin_user(db_session: Session):
    """Create a test admin user"""
    user = User(
        username="admin_ai",
        email="admin_ai@example.com",
        hashed_password=get_password_hash("admin"),
        is_active=True,
        is_admin=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(client: TestClient, test_admin_user: User):
    """Retrieve JWT auth token for admin_ai"""
    response = client.post(
        "/auth/login",
        data={"username": "admin_ai", "password": "admin"},
    )
    return response.json()["access_token"]


@pytest.fixture
def sample_offline_device(db_session: Session):
    """Create a sample offline device for stats and lists"""
    device = DeviceModel(
        name="Router-Test-AI-Offline",
        ip_address="192.168.12.99",
        device_type="router",
        vendor="Cisco",
        status=DeviceStatus.OFFLINE,
        username="admin",
        password=get_password_hash("password")
    )
    db_session.add(device)
    db_session.commit()
    db_session.refresh(device)
    return device


@pytest.fixture
def sample_online_device_with_config(db_session: Session):
    """Create a sample online device with non-secure snmp in configuration to test anomalies"""
    device = DeviceModel(
        name="Switch-Test-AI-Online",
        ip_address="192.168.12.100",
        device_type="switch",
        vendor="Cisco",
        status=DeviceStatus.ONLINE,
        username="admin",
        password=get_password_hash("password")
    )
    db_session.add(device)
    db_session.commit()
    db_session.refresh(device)

    # Add configuration with standard insecure SNMP community
    config = Configuration(
        device_id=device.id,
        version=1,
        content="snmp-server community public RO\ntransport input telnet"
    )
    db_session.add(config)
    db_session.commit()
    return device


def test_ai_suggestions_endpoint(client: TestClient, auth_token: str):
    """Test suggestions are returned properly"""
    response = client.get(
        "/ai/suggestions",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "Колко устройства има в системата?" in data


def test_ai_chat_general_query(client: TestClient, auth_token: str):
    """Test general welcome response is returned in Bulgarian"""
    response = client.post(
        "/ai/chat",
        json={"message": "Здравей, кой си ти?"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "AI Мрежов Асистент" in data["response"]
    assert "suggested_queries" in data


def test_ai_chat_stats_query(client: TestClient, auth_token: str, sample_offline_device: DeviceModel):
    """Test stats query reports real-world device numbers"""
    response = client.post(
        "/ai/chat",
        json={"message": "Колко устройства има в инвентара?"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Общ брой устройства" in data["response"]
    assert "Разпределение по производители" in data["response"]


def test_ai_chat_offline_query(client: TestClient, auth_token: str, sample_offline_device: DeviceModel):
    """Test offline query lists the specific offline device"""
    response = client.post(
        "/ai/chat",
        json={"message": "Кои устройства са офлайн в момента?"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Списък на офлайн мрежовите устройства" in data["response"]
    assert sample_offline_device.name in data["response"]


def test_ai_chat_anomalies_query(client: TestClient, auth_token: str, sample_online_device_with_config: DeviceModel):
    """Test anomalies scan finds the insecure community in config"""
    response = client.post(
        "/ai/chat",
        json={"message": "Сканирай за аномалии по сигурността"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Открити аномалии и заплахи" in data["response"]
    assert "SNMP" in data["response"]
    assert "Telnet" in data["response"]


def test_ai_chat_specific_device_query(client: TestClient, auth_token: str, sample_online_device_with_config: DeviceModel):
    """Test specifically requesting analysis for the Switch-Test-AI-Online"""
    response = client.post(
        "/ai/chat",
        json={"message": f"Анализирай устройство {sample_online_device_with_config.name}"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Детайлен анализ" in data["response"]
    assert sample_online_device_with_config.name in data["response"]


def test_ai_chat_guides_query(client: TestClient, auth_token: str):
    """Test requesting OSPF setup instructions"""
    response = client.post(
        "/ai/chat",
        json={"message": "Как да настроя OSPF на Cisco?"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "Инструкция за конфигуриране на OSPF" in data["response"]
    assert "router ospf" in data["response"]


def test_ai_chat_platform_qa(client: TestClient, auth_token: str):
    """Test requesting platform specific features like back-ups, device addition, Secrets Vault"""
    # 1. Backups Q&A
    response1 = client.post(
        "/ai/chat",
        json={"message": "Как работи бекъпът на конфигурациите?"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response1.status_code == 200
    assert "Бекъпи и Архивиране" in response1.json()["response"]

    # 2. Vault / password rotation Q&A
    response2 = client.post(
        "/ai/chat",
        json={"message": "Разкажи ми за Secrets Vault и ротация на пароли"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response2.status_code == 200
    assert "Secrets Vault" in response2.json()["response"]

    # 3. Adding devices Q&A
    response3 = client.post(
        "/ai/chat",
        json={"message": "Как се добавя устройство?"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response3.status_code == 200
    assert "добавяне на ново устройство" in response3.json()["response"]
