#!/usr/bin/env python3
"""
LANi-Platform - Генератор на Търговски Лицензи (License Generator)
Описание: Използва се за генериране на подписани и криптирани Base64
          лицензионни ключове за клиенти.
"""

import os
import sys
import json
import base64
import argparse
from datetime import datetime

# Import hashes from cryptography for RSA signing if available
try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives.serialization import load_pem_private_key
except ImportError:
    pass

HMAC_SECRET = b"lani-licensing-token-secret-2026-production"


def generate_hmac_license(owner: str, expires_at: str, max_devices: int, features: list) -> str:
    """Generates a license key signed with HMAC-SHA256."""
    import hmac
    import hashlib

    payload = {
        "owner": owner,
        "expires_at": expires_at,
        "max_devices": max_devices,
        "features": features
    }

    # Ensure keys are sorted for deterministic JSON serialization
    payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
    signature = hmac.new(HMAC_SECRET, payload_bytes, hashlib.sha256).hexdigest()

    license_data = {
        "payload": payload,
        "signature": signature,
        "type": "hmac"
    }

    # Encode to Base64
    encoded = base64.b64encode(json.dumps(license_data).encode("utf-8")).decode("utf-8")
    return encoded


def main():
    parser = argparse.ArgumentParser(
        description="LANi-Platform License Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--owner", required=True, help="Име на клиента/фирмата (напр. 'Телеком БГ')")
    parser.add_argument("--devices", type=int, default=100, help="Максимален брой мрежови устройства (по подразбиране: 100)")
    parser.add_argument("--expires", required=True, help="Дата на изтичане във формат YYYY-MM-DD (напр. '2027-08-12')")
    parser.add_argument("--output", help="Файл, в който да бъде записан лиценза (напр. 'license.key')")
    parser.add_argument(
        "--features",
        default="backup,ai_assistant,web_terminal,automation,compliance",
        help="Списък с отключени модули (разделени със запетая)"
    )

    args = parser.parse_args()

    # Validate date
    try:
        datetime.strptime(args.expires, "%Y-%m-%d")
    except ValueError:
        print(f"✗ ГРЕШКА: Невалиден формат на датата '{args.expires}'. Трябва да бъде YYYY-MM-DD.")
        sys.exit(1)

    features_list = [f.strip() for f in args.features.split(",") if f.strip()]

    print("=" * 60)
    print(" LANi-Platform — Генератор на Търговски Лицензи")
    print("=" * 60)
    print(f"• Клиент: {args.owner}")
    print(f"• Лимит Устройства: {args.devices}")
    print(f"• Срок на годност: {args.expires}")
    print(f"• Отключени Модули: {', '.join(features_list)}")
    print("-" * 60)

    # Generate License
    try:
        license_key = generate_hmac_license(
            owner=args.owner,
            expires_at=args.expires,
            max_devices=args.devices,
            features=features_list
        )

        print("\n✔ УСПЕШНО ГЕНЕРИРАН ЛИЦЕНЗИОНЕН КЛЮЧ:")
        print(f"\n{license_key}\n")
        print("-" * 60)

        # Write to file if output is specified
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(license_key)
            print(f"✔ Лицензът е записан успешно във файл: '{args.output}'")
        else:
            print("💡 Съвет: Копирайте целия текстов низ по-горе и го поставете в настройките на LANi-Platform.")

    except Exception as e:
        print(f"✗ Грешка при генериране на лиценза: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
