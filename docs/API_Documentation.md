# API Документация - NCM Платформа

Добре дошли в официалната API документация на NCM Платформата за автоматизация и управление на мрежови конфигурации. Всички заявки изискват `Content-Type: application/json`, освен ако не е посочено друго.

## 1. Управление на Аутентикация и Сесии (`/auth`)

### 1.1 Потребителска Регистрация
* **URL:** `/auth/register`
* **Метод:** `POST`
* **Заявка (Body):**
```json
{
  "username": "admin_user",
  "email": "admin@ncm.local",
  "password": "SecurePassword123!",
  "is_admin": true
}
```
* **Отговор (201 Created):**
```json
{
  "id": 1,
  "username": "admin_user",
  "email": "admin@ncm.local",
  "is_admin": true,
  "is_active": true
}
```

### 1.2 Потребителски Вход (JWT придобиване)
* **URL:** `/auth/login`
* **Метод:** `POST`
* **Заявка (Form-Data):**
  * `username`: `admin_user`
  * `password`: `SecurePassword123!`
* **Отговор (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer"
}
```

---

## 2. Управление на Устройства (`/devices`)
Всички заявки изискват хедър: `Authorization: Bearer <token>`.

### 2.1 Създаване на ново Устройство
* **URL:** `/devices/`
* **Метод:** `POST`
* **Заявка (Body):**
```json
{
  "name": "Core-Switch-01",
  "ip_address": "10.0.0.1",
  "device_type": "switch",
  "vendor": "Cisco",
  "status": "online",
  "username": "cisco_admin",
  "password": "MySuperSecretSSHPassword!",
  "connection_protocol": "ssh",
  "port": 22
}
```
* **Отговор (201 Created):**
```json
{
  "id": 1,
  "name": "Core-Switch-01",
  "ip_address": "10.0.0.1",
  "device_type": "switch",
  "vendor": "Cisco",
  "status": "online",
  "connection_protocol": "ssh",
  "port": 22
}
```
*Забележка: Паролата автоматично се криптира и съхранява сигурно в Secrets Vault чрез Fernet AES-256.*

### 2.2 Тест за Свързаност на Устройство
* **URL:** `/devices/{device_id}/test-connection`
* **Метод:** `POST`
* **Отговор (200 OK):**
```json
{
  "device_id": 1,
  "success": true,
  "connected": true,
  "latency_ms": 12.4,
  "error_message": null
}
```

---

## 3. Валидиране на Конфигурации (`/configurations`)

### 3.1 Валидиране на Команди Преди Пушване (Pre-Push Syntax check)
* **URL:** `/configurations/validate-commands`
* **Метод:** `POST`
* **Заявка (Body):**
```json
{
  "device_id": 1,
  "commands": [
    "interface GigabitEthernet0/1",
    "ip address 192.168.1.1 255.255.255.0",
    "no shutdown"
  ]
}
```
* **Отговор (200 OK):**
```json
{
  "success": true,
  "stage": "completed",
  "errors": [],
  "warnings": []
}
```

---

## 4. Чат с AI Асистент (`/ai`)

### 4.1 Текстов Чат с AI Асистент
* **URL:** `/ai/chat`
* **Метод:** `POST`
* **Заявка (Body):**
```json
{
  "message": "колко устройства са онлайн?"
}
```
* **Отговор (200 OK):**
```json
{
  "response": "В момента в платформата има общо 1 регистрирани устройства, като 1 от тях са със статус **онлайн**."
}
```

### 4.2 Автоматични AI Предложения
* **URL:** `/ai/suggestions`
* **Метод:** `GET`
* **Отговор (200 OK):**
```json
[
  "Кои устройства са офлайн?",
  "Анализирай сигурността на конфигурациите",
  "Покажи последните логове за одит"
]
```
