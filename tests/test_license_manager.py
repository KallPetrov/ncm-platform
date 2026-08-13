import os
import pytest
from app.services.license_manager import LicenseManager


def test_no_license_demo_mode():
    """Verify that with no license, the system falls back to demo mode restrictions."""
    # Ensure no license file exists
    license_path = LicenseManager.get_license_file_path()
    if os.path.exists(license_path):
        os.remove(license_path)

    status = LicenseManager.validate_license()
    assert status["valid"] is False
    assert "ограничена" in status["message"].lower()
    assert status["max_devices"] == 3
    assert "backup" in status["features"]
    assert "ai_assistant" not in status["features"]

    # Verify feature checks
    assert LicenseManager.check_feature_allowed("backup") is True
    assert LicenseManager.check_feature_allowed("ai_assistant") is False
    assert LicenseManager.check_feature_allowed("web_terminal") is False


def test_valid_commercial_license():
    """Verify signature validation and details extraction from a valid license."""
    # Generate a valid test license key (expiring 1 year from now)
    valid_key = LicenseManager.generate_signed_license_for_test(
        owner="Български Мрежови Оператор ООД",
        expires_at="2027-08-12",
        max_devices=500
    )

    # Save and validate
    saved = LicenseManager.save_license(valid_key)
    assert saved is True

    status = LicenseManager.validate_license()
    assert status["valid"] is True
    assert status["owner"] == "Български Мрежови Оператор ООД"
    assert status["max_devices"] == 500
    assert status["expires_at"] == "2027-08-12"
    assert status["days_left"] > 300

    # Verify features are unlocked
    assert LicenseManager.check_feature_allowed("ai_assistant") is True
    assert LicenseManager.check_feature_allowed("web_terminal") is True


def test_expired_commercial_license():
    """Verify that an expired license blocks premium features and falls back to demo limits."""
    # Generate an expired license key
    expired_key = LicenseManager.generate_signed_license_for_test(
        owner="Интернешинал Нетуъркс ЕАД",
        expires_at="2024-01-01",  # Expired
        max_devices=200
    )

    # Save and validate
    saved = LicenseManager.save_license(expired_key)
    assert saved is True

    status = LicenseManager.validate_license()
    assert status["valid"] is False
    assert "изтекъл" in status["message"].lower()
    assert status["max_devices"] == 3  # Fallback to Demo limit

    # Verify features are blocked
    assert LicenseManager.check_feature_allowed("ai_assistant") is False
    assert LicenseManager.check_feature_allowed("web_terminal") is False


def test_tampered_license():
    """Verify that a modified payload fails signature validation."""
    # Create valid key
    valid_key = LicenseManager.generate_signed_license_for_test(
        owner="Тест",
        expires_at="2027-01-01",
        max_devices=10
    )

    # Decode, tamper with payload (change devices to 9999), and save
    import base64
    import json
    decoded_bytes = base64.b64decode(valid_key.encode("utf-8"))
    license_data = json.loads(decoded_bytes.decode("utf-8"))

    # Tamper with the payload
    license_data["payload"]["max_devices"] = 9999

    # Re-encode without regenerating the signature
    tampered_key = base64.b64encode(json.dumps(license_data).encode("utf-8")).decode("utf-8")
    LicenseManager.save_license(tampered_key)

    # Validate
    status = LicenseManager.validate_license()
    assert status["valid"] is False
    assert "подправен" in status["message"].lower()
    assert status["max_devices"] == 0


@pytest.fixture(autouse=True)
def cleanup_license():
    """Cleanup license file before and after test execution."""
    os.environ["LANI_TEST_LICENSE_ENFORCEMENT"] = "1"
    license_path = LicenseManager.get_license_file_path()
    if os.path.exists(license_path):
        os.remove(license_path)
    yield
    if os.path.exists(license_path):
        os.remove(license_path)
    os.environ.pop("LANI_TEST_LICENSE_ENFORCEMENT", None)
