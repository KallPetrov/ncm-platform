import re
from typing import Optional


class SanitizationService:
    """
    Config Data Sanitization & Redaction Engine

    Provides highly reliable regex-based detection and masking of sensitive
    credentials, keys, passwords, and communities across multiple network OS formats.
    """

    # Patterns for Passwords, Secrets, and Keys
    PASSWORD_PATTERNS = [
        # Cisco/HP/Arista passwords and secrets
        (r"(password(?:\s+\d+)?\s+)(\S+)", r"\1<REDACTED_PASSWORD>"),
        (r"(secret(?:\s+\d+)?\s+)(\S+)", r"\1<REDACTED_PASSWORD>"),
        (r"(enable\s+password(?:\s+\d+)?\s+)(\S+)", r"\1<REDACTED_PASSWORD>"),
        (r"(enable\s+secret(?:\s+\d+)?\s+)(\S+)", r"\1<REDACTED_PASSWORD>"),
        # Username password/secret bindings
        (r"(username\s+\S+\s+password(?:\s+\d+)?\s+)(\S+)", r"\1<REDACTED_PASSWORD>"),
        (r"(username\s+\S+\s+secret(?:\s+\d+)?\s+)(\S+)", r"\1<REDACTED_PASSWORD>"),
        # Juniper-style encrypted passwords
        (r"(encrypted-password\s+)(\"\S+\"|\S+)", r"\1<REDACTED_PASSWORD>"),
        # Generic key/value password indicators
        (r"(password\s*=\s*|password:\s*)(\S+)", r"\1<REDACTED_PASSWORD>"),
    ]

    PSK_PATTERNS = [
        # Pre-Shared Keys (IKE/IPsec/WPA)
        (r"(pre-shared-key(?:\s+\d+)?\s+)(\S+)", r"\1<REDACTED_KEY>"),
        (r"(presharedkey(?:\s+\d+)?\s+)(\S+)", r"\1<REDACTED_KEY>"),
        (r"(key(?:\s+\d+)?\s+)(\S+)", r"\1<REDACTED_KEY>"),
        (r"(crypto\s+isakmp\s+key\s+)(\S+)(\s+address\s+\S+)", r"\1<REDACTED_KEY>\3"),
        (r"(crypto\s+ikev2\s+keyring\s+\S+\s+peer\s+\S+\s+pre-shared-key\s+)(\S+)", r"\1<REDACTED_KEY>"),
        # WPA-PSK patterns
        (r"(wpa-psk\s+(?:ascii|hex)?\s*)(\S+)", r"\1<REDACTED_KEY>"),
    ]

    SNMP_PATTERNS = [
        # SNMP Communities and host associations
        (r"(snmp-server\s+community\s+)(\S+)(\s+\S+)?", r"\1<REDACTED_COMMUNITY>\3"),
        (r"(snmp\s+community\s+set\s+\S+\s+name\s*=\s*)(\S+)", r"\1<REDACTED_COMMUNITY>"),
        (r"(snmp-server\s+host\s+\S+\s+version\s+\S+\s+)(\S+)", r"\1<REDACTED_COMMUNITY>"),
    ]

    PRIVATE_KEY_BLOCK_PATTERN = re.compile(
        r"-----BEGIN\s+(?:[A-Z\s]+)?PRIVATE\s+KEY-----\n(.*?)\n-----END\s+(?:[A-Z\s]+)?PRIVATE\s+KEY-----",
        re.DOTALL | re.IGNORECASE
    )

    @classmethod
    def sanitize_configuration(cls, content: str, device_type: Optional[str] = None) -> str:
        """
        Sanitizes and redacts all secrets, passwords, pre-shared keys, private keys,
        and SNMP community strings from the raw configuration text.

        :param content: Raw configuration text.
        :param device_type: Device operating system type (e.g., cisco_ios, juniper, mikrotik).
        :return: Sanitized configuration text.
        """
        if not content:
            return ""

        sanitized = content

        # 1. Redact Private Key blocks (WORM/Air-Gapped standard)
        sanitized = cls.PRIVATE_KEY_BLOCK_PATTERN.sub(
            "-----BEGIN PRIVATE KEY-----\n[REDACTED_PRIVATE_KEY]\n-----END PRIVATE KEY-----",
            sanitized
        )

        # 2. Redact passwords and secrets
        for pattern, replacement in cls.PASSWORD_PATTERNS:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

        # 3. Redact Pre-Shared Keys
        for pattern, replacement in cls.PSK_PATTERNS:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

        # 4. Redact SNMP community strings
        for pattern, replacement in cls.SNMP_PATTERNS:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

        # 5. Clean potential inline SSH keys if we find them inside config blocks
        sanitized = re.sub(
            r"(ssh-rsa\s+)[A-Za-z0-9+/=]{40,}(\s+\S+)?",
            r"\1<REDACTED_SSH_KEY>\2",
            sanitized,
            flags=re.IGNORECASE
        )

        return sanitized
