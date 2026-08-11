from datetime import datetime
import secrets
from sqlalchemy.orm import Session
from cryptography.fernet import Fernet
from app.models.device import Device
from app.services.device_connectivity import DeviceConnectivityService
from app.services.audit import AuditService

import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from app.core.config import settings

# Symmetric dynamic encryption key for Vault Simulation & Encryption at Rest
# Derived from persistent SECRET_KEY to remain fully decryptable across restarts
_salt = b"ncm_salt_vault_secret_2026"
_kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=_salt,
    iterations=100000,
)
_KEY = base64.urlsafe_b64encode(_kdf.derive(settings.SECRET_KEY.encode()))
_CIPHER_SUITE = Fernet(_KEY)


class SecretsVaultService:
    """
    Secrets Vault & Password Rotation Service (Module 3.3)

    Provides secure symmetric encryption (AES/Fernet) for credentials at rest
    and automates scheduled administrative password rotations across network devices.
    """

    @classmethod
    def encrypt_secret(cls, plaintext: str) -> str:
        """Encrypts a plaintext secret (password, community, key)."""
        if not plaintext:
            return ""
        return _CIPHER_SUITE.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    @classmethod
    def decrypt_secret(cls, ciphertext: str) -> str:
        """Decrypts a ciphertext secret back to plaintext."""
        if not ciphertext:
            return ""
        try:
            return _CIPHER_SUITE.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
        except Exception:
            # Fallback if key is re-generated or plaintext was stored
            return ciphertext

    @classmethod
    def rotate_device_password(
        cls, db: Session, device_id: int, new_password: str, is_testing: bool = False
    ) -> dict:
        """
        Automates device password rotation:
        1. Accesses device via secure connectivity.
        2. Configures the new password CLI command.
        3. Encrypts and updates the database record.
        4. Logs the audit activity.
        """
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            return {"success": False, "error": "Device not found"}

        # Generate command for password update (Cisco IOS syntax example)
        rotation_command = f"username {device.username} password {new_password}"

        # 1. Apply password update on real device
        if is_testing:
            success = True
            error_msg = None
        else:
            # Send config command to device
            res = DeviceConnectivityService.send_config_commands(device, [rotation_command])
            success = res["success"]
            error_msg = res.get("error_message")

        if not success:
            return {
                "success": False,
                "error": f"Failed to apply password rotation on device: {error_msg}"
            }

        # 2. Encrypt and save in DB
        encrypted_pass = cls.encrypt_secret(new_password)
        device.password = encrypted_pass
        db.commit()

        # 3. Audit logging
        AuditService.log_action(
            db,
            None,  # system trigger or service account
            "password_rotated",
            resource_type="device",
            resource_id=device.id,
            details=f"Automated password rotated successfully for device {device.name}"
        )

        return {"success": True, "message": "Password rotated and encrypted successfully."}
