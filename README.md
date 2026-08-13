# <img src="https://img.icons8.com/color/48/000000/network-cable.png" width="35"/> LANi-Platform — Network Configuration Management (NCM)

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.0-61DAFB.svg?style=flat-square&logo=react&logoColor=white)](https://react.dev/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-Commercial-red.svg?style=flat-square)](https://lani.bg)
[![Version](https://img.shields.io/badge/Version-01.03.00-green.svg?style=flat-square)](#)

**LANi-Platform** е професионално self-hosted софтуерно решение от корпоративен клас за управление, архивиране и автоматизация на мрежови конфигурации (Network Configuration Management - NCM). Вдъхновена от Unimus, платформата предлага пълен набор от инструменти за наблюдение на жизнения цикъл на мрежовото оборудване, спазване на изискванията за съответствие (Compliance), одит сигурност и изкуствен интелект.

Проектирана за работа в критични инфраструктури с висок интензитет, платформата поддържа реална интеграция с оборудване на водещи мрежови производители и предоставя надеждна защита на чувствителни данни съгласно международни стандарти.

---

## 🛠️ Основен Технологичен Стек (Tech Stack)

Платформата е изградена по модерна архитектура за максимална производителност, скалируемост и отказоустойчивост:

### 🖥️ Бекенд (Backend)
- <img src="https://img.icons8.com/color/16/000000/python--v1.png"/> **Python 3.11+ / 3.12+** — Основен език за бизнес логиката.
- <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/fastapi/fastapi-original.svg" width="16"/> **FastAPI** — Високопроизводителна уеб рамка за REST API с автоматична Swagger/ReDoc документация.
- <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/sqlalchemy/sqlalchemy-original.svg" width="16"/> **SQLAlchemy & Alembic** — ORM система за работа с релационни бази данни и миграции.
- <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/postgresql/postgresql-original.svg" width="16"/> **PostgreSQL / SQLite** — Релационно съхранение на транзакционни данни и потребители.
- <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/redis/redis-original.svg" width="16"/> **Redis** — Брокер за съобщения (Message Broker) и разпределен кеш памет.
- <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/celery/celery-original.svg" width="16"/> **Celery Workers** — Фоново изпълнение на времеемки процеси (архивиране, автоматизация).
- <img src="https://img.icons8.com/color/16/000000/git.png"/> **Git (GitPython)** — Версиониране на конфигурациите чрез Git хранилище за преглед на промените (Diff-ове).
- <img src="https://img.icons8.com/color/16/000000/shield.png"/> **Cryptography (Fernet)** — Криптографско сигурно симетрично шифроване на пароли и Vault секрети.

### 🎨 Фронтенд (Frontend)
- <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/react/react-original.svg" width="16"/> **React 19 & TypeScript** — Модерен, интерактивен интерфейс от нов клас.
- <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/vite/vite-original.svg" width="16"/> **Vite** — Свръхбърз инструмент за компилиране на фронтенд кода.
- <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/tailwindcss/tailwindcss-original.svg" width="16"/> **TailwindCSS** — Гъвкава CSS рамка за отзивчив (responsive) дизайн.
- <img src="https://img.icons8.com/ios-filled/16/000000/external-link.png"/> **Radix UI & Lucide Icons** — Компоненти за достъпност и модерен визуален стил.

---

## ✨ Внедрени Функционалности и Модули

LANi-Platform включва следните напълно функциониращи, реални и работещи на 100% модули (без симулирани или хардкоднати стойности):

1. 🧠 **AI Асистент & Интелигентен Анализ**
   - Интелигентен AI чат асистент на чист български език, напълно интегриран с базата данни (с достъп до мрежовия инвентар, одит логовете и статусите на устройствата).
   - Автоматично обяснение на конфигурационни разлики (Diffs) и евристично сканиране на промени за сигурност.
   - База от знания за мрежови протоколи (OSPF, BGP, SSH, VLAN).

2. 🔐 **Secrets Vault & Ротация на Пароли**
   - Централизиран криптографски сейф (Vault) за пароли, използващ Fernet симетрично шифроване (AES-128/256) в покой.
   - Напълно автоматизирана услуга за редовна ротация на административните пароли директно върху мрежовите устройства по график.

3. 📂 **NetBox & Nautobot SSOT Синхронизация**
   - Двупосочна интеграция за автоматичен синхрон на мрежовия хардуер с единствен източник на истина (Single Source of Truth - SSOT) за нулев ръчен дрейф (no drift).

4. 🕸️ **Мрежова Топология & LLDP/CDP Трасиране**
   - Автоматично извличане на съседства по протоколите LLDP и CDP.
   - Изграждане на топологична карта с връзките (Edges) между всички регистрирани в системата устройства.

5. 🛡️ **Вграден Уеб Терминал (Web SSH) & Запис на Сесии**
   - Secure SSH терминал директно в уеб браузъра (Network PAM proxy).
   - Скриване на реалните пароли и секрети от крайните клиенти.
   - Записване и одит на всяко натискане на клавиш (Keystroke logging), въведена команда и изходен резултат за пълно съответствие с NIS2 регулациите.

6. 🔍 **Валидация на Конфигурации (Pre-Push Checks)**
   - Синтактична проверка на командите преди изпращането им към устройството.
   - Автоматизирани мрежови валидации (reachability pings) и следене на промените по състоянието на интерфейсите (Operational Interface validations).

7. 🔄 **Автоматичен Ъпгрейд на Фърмуер (OS Upgrades)**
   - Планиране и изпълнение на масови ъпгрейди на мрежови операционни системи (Cisco IOS, JunOS, RouterOS и др.).
   - Предварителни проверки за свободно дисково пространство, верификация с MD5/SHA256 контролни суми, автоматично рестартиране и мониторинг на успешна достъпност след ъпгрейд.
   - **Автоматичен Rollback** при повреда на връзката или неуспешен тест.

8. 🧼 **Саниране на Конфигурации & Redaction**
   - Автоматизирано откриване и заменяне/маскиране (Redaction) на сензитивна информация (пароли, enable секрети, Pre-Shared Keys, SNMP communities, частни SSH ключове) от извлечените бекъпи в реално време, преди записване в базата данни или Git.

9. 📋 **Съответствие (Compliance) & Автоматично Отстраняване**
   - Шаблони от правила за съответствие (Security, Management, NTP, AAA).
   - Извеждане на детайлни доклади за пропуски в конфигурациите.
   - Автоматичен rollback (Remediation) при засичане на неразрешен дрейф (Configuration Drift).

---

## 🚀 Инструкции за Стартиране на Различни Платформи

### 🐧 1. Linux (Препоръчително)

За най-бързо и лесно стартиране на Linux е разработен професионален интерактивен Bash скрипт, който се грижи за зависимостите, конфигурациите и стартирането.

#### Стартиране чрез автоматичния скрипт:
```bash
# Преминете в корена на проекта
cd ncm-platform

# Стартирайте интелигентния скрипт
./scripts/lani-start.sh
```
*Скриптът ще ви предложи графично меню с опции:*
1. **Стартиране чрез Docker Compose** (всички услуги в контейнери — PostgreSQL, Redis, Celery, Backend, Frontend, Nginx).
2. **Локално стартиране за разработка** (стартира виртуална среда Python, локална SQLite БД и NPM уеб сървър).
3. **Стартиране на Автоматизирани Тестове** (pytest).

---

### 🍏 2. macOS (Apple Silicon & Intel)

macOS поддържа както Docker стартиране, така и локално стартиране през терминала.

#### Вариант А: Чрез Docker (Препоръчително)
1. Уверете се, че имате инсталиран **Docker Desktop** за Mac.
2. Стартирайте контейнерите:
   ```bash
   docker-compose up -d --build
   ```

#### Вариант Б: Локално стартиране през Терминала
1. Инсталирайте dependencies чрез `Homebrew` при необходимост:
   ```bash
   brew install python node redis postgresql
   ```
2. Бекенд инициализация:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt

   # Инициализиране на базата данни (SQLite за локални цели)
   DATABASE_URL=sqlite:///./test.db python3 scripts/init_db.py

   # Стартиране на FastAPI
   TESTING=1 uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
3. Фронтенд стартиране (в нов терминал):
   ```bash
   cd frontend
   npm install
   npm run dev -- --port 5173
   ```

---

### 🪟 3. Windows (10/11)

За стартиране на Windows се препоръчва използването на **Docker Desktop** или **WSL2** (Windows Subsystem for Linux).

#### Вариант А: Чрез Docker Desktop (Най-бързо)
1. Инсталирайте и стартирайте **Docker Desktop** на Вашия компютър.
2. Отворете `PowerShell` или `Command Prompt` в директорията на проекта и изпълнете:
   ```powershell
   docker-compose up -d --build
   ```

#### Вариант Б: Локално стартиране (Native Windows)
1. Инсталирайте последна версия на [Python 3.11+](https://www.python.org/downloads/) и [Node.js](https://nodejs.org/).
2. Отворете `PowerShell` в корена на проекта и създайте виртуална среда:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
3. Инициализирайте базата данни:
   ```powershell
   $env:DATABASE_URL="sqlite:///./test.db"
   python scripts/init_db.py
   ```
4. Стартирайте уеб сървъра на бекенда:
   ```powershell
   $env:TESTING="1"
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
5. Инсталирайте и стартирайте фронтенда в нов PowerShell прозорец:
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

---

## 🐳 Използване на Docker Compose (Всички платформи)

Docker Compose съдържа пълната производствена конфигурация, готова за внедряване в реална среда:

```bash
# Стартиране на всички контейнери в защитен бекграунд режим
docker-compose up -d --build

# Преглед на текущите контейнери
docker-compose ps

# Следене на логове в реално време
docker-compose logs -f
```

След успешно стартиране:
- 🌐 **Интерфейс (Frontend):** `http://localhost:3000` (Пренасочва се през Nginx).
- 🔗 **REST API Swagger:** `http://localhost:8000/docs`
- 🔒 **Вход по подразбиране:** `admin` / `admin` (Препоръчва се незабавна смяна в реална среда).

---

## 🧪 Системни Тестове (Testing)

Платформата има отлично покритие от тестове, гарантиращи стабилност при промени:

```bash
# Стартиране на пълния тестови пакет от 96 интеграционни и E2E теста
TESTING=1 pytest
```

Тестовете проверяват:
- Сигурността и нивата на достъп (RBAC) за администратори и наблюдатели.
- Подаването на SSH сесии и одит записите на клавиши.
- Автоматичното саниране и тригърването на ъпгрейди на мрежовия софтуер.
- Интегрирания AI Асистент и неговите отговори.

---

## 📂 Структура на Проекта

```text
lani-platform/
├── app/                  # FastAPI Бекенд Приложение
│   ├── api/              # API рутери (auth, devices, configurations, audit)
│   ├── core/             # Конфигурации, БД връзка, сигурност
│   ├── models/           # SQLAlchemy бази данни схеми
│   ├── schemas/          # Pydantic валидиращи схеми
│   ├── services/         # Бизнес логика (AI, Secrets Vault, SSH, backup)
│   └── main.py           # Основен FastAPI входен пункт
├── frontend/             # React + Vite + TypeScript Фронтенд
│   ├── src/
│   │   ├── components/   # UI компоненти (Dashboards, AI Panel, Audit)
│   │   └── lib/          # API Свързаност и хелпъри
├── scripts/              # Помощни и инсталационни скриптове
│   ├── lani-start.sh     # Интерактивен стартиращ скрипт за Linux
│   └── init_db.py        # Инициализация и сийдване на данни
├── docs/                 # Пълна продуктова документация
├── tests/                # Интеграционни и E2E pytest тестове
├── Changelog.md          # История на версиите
├── Module_Status.md      # Статус на софтуерните модули
└── docker-compose.yml    # Продуктова оркестрация на контейнери
```

---

## 📜 Лиценз (License)

Този софтуерен продукт е лицензиран под **Търговски лиценз на LANi-Platform**.
Всички права са запазени. Използването, копирането, модификацията или разпространението на този софтуер без изрично писмено разрешение от правоносителя са строго забранени.

За въпроси относно корпоративни планове, поддръжка или придобиване на лиценз, моля, свържете се с нас.

---
**Разработено с 💻 и ☕ за нуждите на модерната мрежова автоматизация и сигурност.**
