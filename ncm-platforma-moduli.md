# Модули на Network Configuration Management (NCM) платформа

Пълен списък с модули за разработка на собствена NCM платформа (тип Unimus, SolarWinds NCM, Oxidized) — от основни (задължителни за MVP) до разширени/екстра модули, които разграничават платформата от базов инструмент до пълноценен enterprise продукт.

---

## 1. Основни модули (Core — задължителни за всяка NCM платформа)

### 1.1 Device Connectivity Layer
- **SSH/Telnet клиент** — връзка към мрежовите устройства чрез стандартни протоколи
- **SNMP клиент** — за discovery и базов мониторинг (v1/v2c/v3)
- **Vendor/device adapters** — абстракция за различните CLI синтаксиси (Cisco IOS/NX-OS, Juniper JunOS, MikroTik RouterOS, HP/Aruba, Fortinet, Palo Alto и т.н.)
- **Connection pooling** — управление на паралелни сесии без претоварване на мрежата
- **Prompt detection / paging handling** — справяне с "--More--", различни CLI режими (user/enable/config mode)

### 1.2 Device Inventory (CMDB-lite)
- База данни с устройства: IP, hostname, модел, vendor, OS версия, локация
- Групиране по сайт, тип, отдел, критичност
- Custom tags / labels за филтриране
- Import/export (CSV, Excel, API)

### 1.3 Configuration Backup Engine
- Периодично автоматично изтегляне на running-config / startup-config
- Ръчен (on-demand) backup при нужда
- Съхранение с версиониране (git backend или собствена DB схема)
- Diff между версии (текстово и визуално)
- Retention policy — колко версии/за колко време се пазят

### 1.4 Change Detection & Notifications
- Периодична проверка (hash сравнение) на конфигурации
- Реално-времеви detection при промяна
- Известия: email, Slack, Telegram, webhook, Pushover
- Change log с автор (ако е известен), timestamp, diff preview

### 1.5 Scheduler / Job Engine
- Периодично изпълнение на задачи (cron-подобен синтаксис)
- Опашка за задачи с retry логика при неуспех
- Паралелно изпълнение с контрол на конкурентността
- История на job-ове (успешни/неуспешни, логове)

### 1.6 Web GUI (Dashboard)
- Списък с устройства и статус
- Diff viewer (side-by-side или unified)
- История на конфигурации по устройство
- Статус на последен backup/job
- Търсене в конфигурации (global search)

### 1.7 Authentication & Credential Management
- Криптирано съхранение на пароли/SSH ключове (at rest, напр. AES/Fernet)
- Credential profiles — многократно ползване на един набор данни за много устройства
- Поддръжка на SSH key-based auth освен парола

---

## 2. Автоматизация и промени (Automation)

### 2.1 Template Engine
- Jinja2 (или подобен) за генериране на конфигурации от темплейти
- Variables/parameters per device или per group
- Preview на генерирана конфигурация преди push

### 2.2 Mass Configuration Push
- Изпращане на команди/конфигурации към много устройства едновременно
- Dry-run режим (симулация без реално прилагане)
- Rollback при неуспех

### 2.3 Firmware / OS Upgrade Automation
- Масов ъпгрейд на фърмуер по разписание
- Проверка на версии преди/след
- Автоматичен rollback при провален upgrade

### 2.4 Compliance / Rule Engine
- Дефиниране на политики (напр. "всички устройства трябва да имат NTP сървър X")
- Автоматична проверка на всички устройства срещу правилата
- Compliance report с violations

### 2.5 Configuration Validation
- Syntax checking преди push (да не се качи счупена конфигурация)
- Pre-change / post-change validation (пинг тестове, проверка на interface статус)

---

## 3. Сигурност и достъп (Security & Access)

### 3.1 Role-Based Access Control (RBAC)
- Роли: admin, operator, viewer, auditor
- Ограничения по устройство/група (напр. екип X вижда само сайт Y)
- Двуфакторна автентикация (2FA/MFA)

### 3.2 Audit Log
- Пълен log кой какво е направил, кога, от къде (IP)
- Immutable log (защита от изтриване/подправяне)
- Export за compliance цели (NIS2, ISO 27001, PCI-DSS)

### 3.3 Secrets Management Integration
- Интеграция с HashiCorp Vault, AWS Secrets Manager и др. за enterprise клиенти
- Ротация на пароли по разписание

### 3.4 Session Recording
- Запис на CLI сесии, отворени през платформата (за одит и troubleshooting)

---

## 4. Интерфейси и интеграции

### 4.1 REST API
- Пълен API за всички операции (устройства, backup, jobs, diff)
- API keys / OAuth за достъп
- Rate limiting

### 4.2 Webhooks
- Изходящи известия при събития (промяна, неуспешен job, compliance violation)

### 4.3 Интеграции с трети страни
- Ticketing системи (Jira, ServiceNow) — автоматично създаване на ticket при неоторизирана промяна
- ChatOps (Slack, MS Teams, Telegram bots)
- SIEM интеграция (Splunk, ELK) за security monitoring
- CI/CD pipelines (GitLab CI, Jenkins) — конфигурациите като код (NetDevOps)

### 4.4 CLI / SDK
- Команден интерфейс за DevOps автоматизация
- Python/Go SDK за custom скриптове

---

## 5. Мониторинг и видимост (отвъд самия config management)

### 5.1 Basic Network Monitoring
- Ping/SNMP polling за up/down статус
- Interface utilization графики
- Alert при недостъпност на устройство

### 5.2 Topology Mapping
- Автоматично изграждане на мрежова топология (LLDP/CDP discovery)
- Визуална карта на връзките между устройства

### 5.3 Reporting & Analytics
- Периодични отчети (седмични/месечни) за промени, compliance статус
- Dashboard с KPI-та (брой backup-и, % compliance, честота на промени)
- Export в PDF/Excel

---

## 6. Екстра / разширени модули (диференциращи фактори)

Тези модули не са задължителни за MVP, но превръщат платформата от "поредния Oxidized клонинг" в конкурентен продукт.

### 6.1 AI-асистирано анализиране на конфигурации
- Автоматично обяснение на diff-ове на естествен език ("тази промяна отваря порт 22 към целия интернет")
- Anomaly detection — засичане на необичайни промени чрез ML модел, обучен на историческите данни
- AI chatbot за питания от типа "кои устройства нямат конфигуриран NTP"

### 6.2 Predictive Maintenance
- Анализ на логове/метрики за предсказване на хардуерен отказ преди да се случи
- Препоръки за ъпгрейд на базата на end-of-life/end-of-support дати на устройствата

### 6.3 Multi-tenancy
- Пълна изолация между клиенти/отдели в една инсталация — критично за MSP (Managed Service Providers)
- White-labeling за MSP клиенти

### 6.4 Configuration Drift Auto-Remediation
- Автоматично връщане на конфигурация към "known good" състояние при засечена неоторизирана промяна, без човешка намеса (с configurable approval workflow)

### 6.5 Network-as-Code / GitOps Workflow
- Конфигурациите се пазят в Git repo като single source of truth
- Pull request workflow — промени в конфигурация минават през code review преди push
- Автоматична синхронизация между Git state и реалното мрежово състояние

### 6.6 Disaster Recovery Orchestration
- Едно-кликов пълен рестор на цяла мрежа (не само едно устройство) при масов инцидент
- Симулация на DR сценарии (test restore без да пипаш production)

### 6.7 Vulnerability & CVE Correlation
- Автоматично съпоставяне на инсталирани OS версии с публични CVE бази данни
- Приоритизиране на ъпгрейди по критичност на уязвимостта

### 6.8 Advanced Compliance Frameworks
- Вградени шаблони за NIS2, PCI-DSS, ISO 27001, CIS Benchmarks
- Автоматично генериране на compliance доклади за одитори

### 6.9 Change Approval Workflow (ITSM-style)
- Multi-step approval преди прилагане на промяна (maker-checker принцип)
- Интеграция с change advisory board (CAB) процеси

### 6.10 Mobile App
- Известия и базов преглед на статус от телефон
- Push notification при критична промяна или инцидент

### 6.11 Custom Plugin/Extension System
- API за трети страни разработчици да пишат собствени plugins (нови vendor adapters, custom reports)
- Marketplace за споделяне на community-написани adapters

### 6.12 Historical Trend Analysis
- Дългосрочен анализ на честота на промени по устройство/екип
- Correlation между промени и инциденти (change-caused outage detection)

### 6.13 IPAM Integration (IP Address Management)
- Съвместна работа или вградена функционалност за управление на IP адресно пространство
- Автоматична проверка на съответствие между конфигурация и IPAM записи

### 6.14 Zero-Touch Provisioning (ZTP)
- Автоматично конфигуриране на изцяло ново устройство при първо включване в мрежата, без ръчна намеса

---

## Препоръчителна приоритизация

| Фаза | Модули |
|---|---|
| **MVP (фаза 1)** | 1.1 – 1.7 (Core) |
| **Фаза 2** | 2.1 – 2.5 (Automation), 3.1 – 3.2 (базова сигурност) |
| **Фаза 3** | 4.1 – 4.3 (интеграции), 5.1 – 5.3 (мониторинг) |
| **Фаза 4 (диференциация)** | Избрани модули от секция 6, според целевия пазар (MSP → multi-tenancy; enterprise → compliance frameworks; DevOps-ориентирани клиенти → GitOps workflow) |

---

*Документът е предназначен като референтна рамка за архитектурно планиране на собствена NCM платформа.*
