#!/usr/bin/env python3
"""
NCM Platform - Скрипт за Одит на Сигурността и Подсилване (Security Hardening).
Анализира текущата инсталация за потенциални рискове и генерира подробен доклад.
"""

import os
import sys

def audit_security():
    print("=== [NCM Security Hardening Audit Started] ===")
    warnings = 0
    passed = 0

    # 1. Проверка на .env файла
    if not os.path.exists(".env"):
        print("[КРИТИЧНО] липсва .env файл в корена на проекта!")
        warnings += 1
    else:
        passed += 1
        with open(".env", "r") as f:
            env_content = f.read()

            # Проверка за SECRET_KEY по подразбиране
            if "fallback_secret_key_for_dev_only" in env_content:
                print("[ПРЕДУПРЕЖДЕНИЕ] Използва се SECRET_KEY по подразбиране! Моля, генерирайте уникален секретен ключ.")
                warnings += 1
            else:
                passed += 1

            # Проверка за сигурност на PostgreSQL паролата
            if "POSTGRES_PASSWORD=postgres" in env_content:
                print("[ПРЕДУПРЕЖДЕНИЕ] Използва се подразбиращата се парола за PostgreSQL ('postgres')!")
                warnings += 1
            else:
                passed += 1

    # 2. Проверка на правата на файловете
    for sensitive_file in [".env", "test.db", "alembic.ini"]:
        if os.path.exists(sensitive_file):
            mode = os.stat(sensitive_file).st_mode
            # Предупреждение за прекалено свободни права (група/други да могат да пишат/четат)
            if mode & 0o007:
                print(f"[ПРЕДУПРЕЖДЕНИЕ] Файлът '{sensitive_file}' има прекалено свободни права за четене/запис от външни потребители!")
                warnings += 1
            else:
                passed += 1

    # 3. Проверка на Git конфигурационните файлове
    configs_dir = "./storage/configs"
    if os.path.exists(configs_dir):
        passed += 1
    else:
        print("[ПРЕДУПРЕЖДЕНИЕ] Липсва папка за съхранение на конфигурации в Git ('./storage/configs')")
        warnings += 1

    print("\n=== [Резултат от Одита] ===")
    print(f"Преминали проверки: {passed}")
    print(f"Открити предупреждения/рискове: {warnings}")

    if warnings > 0:
        print("\n[СЪВЕТ] Моля, прегледайте препоръките по-горе, за да подсигурите Вашата NCM платформа за производство!")
        sys.exit(1)
    else:
        print("\n[ОТЛИЧНО] Платформата отговаря на основните производствени изисквания за сигурност!")
        sys.exit(0)

if __name__ == "__main__":
    audit_security()
