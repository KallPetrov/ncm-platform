# Архитектурна рамка и модули на Network Configuration & Automation Management (NCM) платформа

Пълен, изчерпателен референтен списък с модули за разработка на съвременна **NCM / NetDevOps / Intent-Based Networking** платформа (тип Unimus, SolarWinds NCM, Cisco Catalyst Center, Forward Networks, NetBrain). 

Документът обхваща цялостната еволюция на системата — от основните задължителни модули за MVP до най-съвременните Next-Gen, AI и симулационни среди.

---

## 1. Основни модули (Core — задължителни за MVP)

### 1.1 Device Connectivity Layer
- **SSH/Telnet клиент** — криптирана връзка към мрежовите устройства чрез стандартни протоколи.
- **SNMP клиент** — за auto-discovery и базов мониторинг (v1/v2c/v3).
- **Vendor / Device Adapters** — абстракционен слой за поддръжка на различни CLI синтаксиси (Cisco IOS/NX-OS/XE, Juniper JunOS, MikroTik RouterOS, HP/Aruba, Fortinet FortiOS, Palo Alto PAN-OS, Huawei VRP, Arista EOS).
- **Connection Pooling & Rate Limiting** — управление на паралелни сесии без претоварване на мрежовото оборудване или CPU-то на устройствата.
- **Prompt Detection & Paging Handling** — справяне с `--More--`, автоматично превключване между CLI среди (`user`, `enable`, `config` режими).

### 1.2 Device Inventory (CMDB-lite)
- База данни с устройства: IP, Hostname, модел, вендор, OS версия, сериен номер, локация/шкаф.
- Иерархично групиране по сайт, сграда, отдел, слой (Access, Distribution, Core), критичност.
- Custom Tags & Labels за филтриране и динамични групи.
- Гъвкав Import/Export (CSV, JSON, Excel, REST API).

### 1.3 Configuration Backup Engine
- Периодично автоматично изтегляне на `running-config` и `startup-config`.
- Ръчен (on-demand) backup при нужда или преди планирана промяна.
- Версионирано съхранение (Git backend или оптимизирана база данни).
- Diff Engine — сравнение между две версии (текстово side-by-side, unified diff, визуално с оцветяване).
- Retention Policy — конфигурируема политика за съхранение (напр. пази последните N версии или за период от X месеца).

### 1.4 Change Detection & Notifications
- Периодична проверка и засичане на промени чрез Hash сравнение на конфигурационния файл.
- Реално-времеви (real-time) change detection (чрез слушане на Syslog / SNMP Traps за `CONFIG_CHANGE` събития).
- Известия по канали: Email, Slack, MS Teams, Telegram, Webhook, Pushover.
- Change Log с детайли: автор (ако е засечен от syslog), timestamp, diff преглед.

### 1.5 Scheduler / Job Engine
- Периодично изпълнение на задачи с cron-подобен синтаксис.
- Опашка за задачи (Task Queue) с retry логика и интелигентно изчакване при неуспех.
- Паралелно изпълнение с контрол на конкурентността (Concurrency control per site/vendor).
- Пълна история на изпълнените задачи (успешни/неуспешни, подробни логове).

### 1.6 Web GUI (Dashboard & Management Console)
- Дашборд със статус на устройствата, здраве на мрежата и последните извършени backups/jobs.
- Advanced Diff Viewer (Side-by-side, Unified, оцветяване на добавени/изтрити линии).
- История на конфигурациите по устройство с опция за бърз преглед и изтегляне.
- Глобално търсене (Global Search) в съдържанието на всички конфигурации (търсене на IP-та, VLAN-и, съвпадения по регулярни изрази/Regex).

### 1.7 Authentication & Credential Management
- Криптирано съхранение на пароли, enable пароли и SSH keys (at rest с AES-256 / Fernet).
- Credential Profiles — дефиниране на профили с пароли, използвани повторно за групи устройства.
- Поддръжка на SSH Key-based автентикация и SSH passphrase.

### 1.8 Config Data Sanitization & Redaction Engine
- Автоматично засичане и маскиране/криптиране на чувствителни данни (пароли, Pre-Shared Keys, private keys, SNMP communities) в изтеглената конфигурация.
- Защита от изтичане на тайни при визуализация в GUI, изпращане към external Git, SIEM или AI модели.

---

## 2. Архитектура и разпределена инфраструктура (Platform Infrastructure)

### 2.1 Distributed Remote Collectors / Proxies (Remote Agents)
- Леки агенти (Pollers/Proxies), разположени в географски отдалечени офиси, изолирани DMZ сегменти или различни Cloud VPC-та.
- Центрирана комуникация (outbound TLS тунел от агента към централния сървър), спестяваща отварянето на директен SSH/SNMP достъп през интернет.

### 2.2 High Availability (HA) & Clustering
- Клъстеризация на контролния панел (Control Plane) и worker възлите.
- Автоматично превключване при отпад (Failover) и балансиране на натоварването (Load Balancing) при големи мрежи (10,000+ устройства).

### 2.3 Built-in Web Terminal & Network PAM (Privileged Access Management Proxy)
- Отваряне на SSH сесия към мрежово устройство директно през уеб браузъра (Web SSH).
- Без разкриване на реалната парола пред инженера (NCM инжектира данните от Vault).
- Пълен одит: Keystroke logging и запис на сесията (Session Recording & Replay) за одит и съответствие.

---

## 3. Автоматизация, Промени и Безопасност (Automation & Guardrails)

### 3.1 Template Engine
- Шаблониране на конфигурации (Jinja2 / Mustache) за генериране на стандартизирани настройки.
- Променливи (Variables & Parameters) на ниво устройство, група или глобално.
- Preview на генерираната конфигурация (Dry-run) преди изпращане към устройството.

### 3.2 Mass Configuration Push & Safety Guardrails
- Изпращане на команди или конфигурационни блокове към стотици устройства едновременно.
- Dry-Run режим — симулация без реално прилагане (ако вендорът поддържа `check` режим).
- Автоматичен Rollback при грешка по време на изпълнение.
- **Blast Radius & Topology-Aware Rollout (Phased Rollouts):** Изпълнение на промените на вълни (напр. 5% Canary devices -> тест -> 25% -> 100%). Автоматично подреждане по топология: промените се прилагат първо на периферните (Access) устройства и най-накрая на Core/Gateway за предотвратяване на изолация.

### 3.3 Firmware / OS Upgrade Automation
- Масов ъпгрейд на фърмуер по разписание.
- Pre-checks & Post-checks (проверка на свободна памет, MD5/SHA256 хеш на изображението, състояние на интерфейси и рутинг преди/след).
- Автоматичен rollback към предишното флаш изображение при неуспешно зареждане.

### 3.4 Compliance & Rule Engine
- Дефиниране на политики за сигурност и стандартизация (напр. "всички суичове трябва да имат NTP сървър X, disabled Telnet, конфигуриран Syslog").
- Автоматична проверка на устройствата спрямо правилата.
- Compliance доклади с детайлизация на нарушените правила (Violations) и инжектиране на Коригиращи скриптове (Remediation Scripts).

### 3.5 Maintenance Windows & Change Freeze Periods
- Конфигурируеми прозорци за поддръжка (Maintenance Windows).
- Автоматично блокиране на масови автоматизирани задачи по време на критични за бизнеса периоди (Change Freeze / Blackout periods).

### 3.6 Stale & Unused Config Cleanup Engine
- Автоматичен одит за излишни конфигурационни блокове: неизползвани ACL правила, празни VLAN-и, остарели статични рутове, неизползвани object groups.

---

## 4. Модерни и Хибридни Мрежови Интерфейси (Modern & Cloud Networks)

### 4.1 Model-Driven Management (NETCONF / RESTCONF / gNMI / YANG)
- Поддръжка на структурирано управление чрез YANG модели и OpenConfig вместо нестабилен CLI парсинг.
- Атомни транзакции (`commit`, `rollback`, `candidate configuration`) на ниво протокол.

### 4.2 Cloud, Controller & SD-WAN Adapters (API-Driven NCM)
- Интеграция с контролерно управлявани и Cloud среди (Cisco Meraki, Cisco Viptela SD-WAN, Fortinet FortiManager, Palo Alto Panorama, AWS VPCs, Cloudflare, Tailscale).
- Изтегляне и управление на политики през REST / GraphQL APIs.

### 4.3 Certificate & PKI Lifecycle Management
- Автоматична инвентаризация на инсталираните SSL/TLS и IPsec (IKE/X.509) сертификати в мрежата.
- Известия за изтичащи сертификати (напр. 30 дни предварително) и автоматизирано подновяване през SCEP, EST или ACME протоколи.

---

## 5. Управление на Активи, Лицензи и Портове (Asset & Lifecycle Visibility)

### 5.1 Hardware Lifecycle & EoX (End-of-Life / End-of-Sale) Tracking
- Интеграция с вендорски API-та (напр. Cisco EoX API) за автоматично съпоставяне на серийните номера с официалните дати за прекратяване на продажба и поддръжка.
- Анализ на остаряването на хардуерния парк и планиране на бюджети за подмяна.

### 5.2 License & Contract Management
- Следене на лицензионния статус (Cisco Smart Licensing, Fortinet Subscriptions, Palo Alto Feature Licenses).
- Управление на сервизни договори (Cisco Smart Net Total Care, вендорски гаранции) с аларми при изтичане.

### 5.3 Interface & Port Drift Audit
- Проследяване на промени по интерфейсите (VLAN промени, admin status, speed/duplex, PoE консумация).
- Засичане на неизползвани/замръзнали портове (без link/трафик от 90+ дни) за освобождаване на капацитет.

---

## 6. Сигурност, Одит и Откриване (Security & Discovery)

### 6.1 Role-Based Access Control (RBAC & MFA)
- Детайлни роли: Admin, Network Engineer, Operator, Viewer, Auditor.
- Ограничение на достъпа по обхват (Scope/Tenant) — екип А вижда и редактира само сайт X.
- Вградена поддръжка за Multi-Factor Authentication (2FA/MFA — TOTP, WebAuthn/Passkeys, SAML/OIDC SSO).

### 6.2 Audit Log (Immutable Audit)
- Подробен лог: КОЙ какво е променил, КОГА, ОТ КЪДЕ (IP адрес) и КАКЪВ е бил резултатът.
- Защита от подправяне/изтриване (Immutable log engine).
- Експорт на съвместими доклади за ISO 27001, NIS2, PCI-DSS, SOC2.

### 6.3 Secrets Management Integration
- Интеграция с enterprise среди за управление на тайни: HashiCorp Vault, AWS Secrets Manager, Azure Key Vault.
- Автоматична ротация на пароли за мрежово оборудване по разписание.

### 6.4 Rogue Device Detection & Syslog Auto-Discovery
- Слушане за нови устройства чрез Syslog, SNMP Traps, CDP/LLDP съседи и ARP таблици.
- Автоматично откриване и уведомяване при включване на неоторизирано оборудване в мрежата.

### 6.5 Immutable WORM Config Archival & Air-Gapped Vault
- Възможност за съхранение на архив от конфигурации в WORM (Write Once, Read Many) или Air-Gapped изолиран архив за пълно възстановяване при разрушителни кибератаки (Ransomware).

---

## 7. Интерфейси, Интеграции и SSOT (Interfaces & Integrations)

### 7.1 REST API & GraphQL
- Пълен API достъп до абсолютно всички функционалности на платформата.
- Автентикация с API Keys, OAuth2, JWT.
- Rate limiting & API throttling за стабилност.

### 7.2 Outbound Webhooks & ChatOps
- Изходящи уебхукове при настъпване на събития.
- Интеграция с ChatOps (Slack, MS Teams, Telegram бота за бързи проверки и изпълнение на одобрени команди).

### 7.3 Интеграция с ITSM, SIEM и CI/CD
- **ITSM / Ticketing:** Jira, ServiceNow (автоматично отваряне на Incident/Change Ticket при неотчетена промяна).
- **SIEM:** Splunk, Elastic/ELK, QRadar (изпращане на audit & change събития).
- **CI/CD:** GitLab CI, GitHub Actions, Jenkins за спазване на NetDevOps / Config-as-Code практики.

### 7.4 Single Source of Truth (SSOT) Integration
- Двупосочна синхронизация с **NetBox** или **Nautobot**.
- Система за проверка съответствието между софтуерно дефинираното намерение в SSOT и реалното състояние на устройствата.

### 7.5 CLI Tool & SDKs
- Собствена CLI либ/инструмент за администратори.
- Python SDK (`pip install my-ncm-sdk`) и Go SDK за разработчици.

---

## 8. Мониторинг, Топология и Симулации (Observability & Simulation)

### 8.1 Network Observability & Telemetry Integration
- Ping / SNMP Polling за достъпност (Up/Down) и интерфейсен трафик.
- gRPC / gNMI Streaming Telemetry за събиране на метрики в реално време без забавяне.

### 8.2 Topology Mapping & Dynamic Visualization
- Автоматично изграждане на мрежова топология (Layer 2 / Layer 3) чрез CDP, LLDP, OSPF, BGP данни.
- Динамична интерактивна карта с визуализация на връзките, статусите и промените по трасето.

### 8.3 Digital Twin & Pre-Push Simulation
- Интеграция с контейнерни и емулационни среди (**Containerlab**, GNS3, EVE-NG, Cisco CML).
- Автоматично изграждане на виртуален дубъл (Digital Twin) на реалната мрежа.
- Автоматично тестване на промените върху виртуалния дубъл с pyATS / Robot Framework преди реално прилагане в production.

### 8.4 Reporting & Analytics
- Периодични отчети за промени, compliance съответствие, уязвимости.
- Персонализирани KPI табла и експорт в PDF, Excel, CSV.

---

## 9. Иновативни и Разширени Next-Gen Модули (AIOps & Next-Gen Differentiation)

### 9.1 Intent-Based Networking (IBN) Engine
- Дефиниране на правила на високо бизнес ниво (напр. "Зона А няма достъп до Зона Б").
- Компилатор, който автоматично превежда бизнес правилата в съответните вендорски настройки.

### 9.2 Formal Verification Engine (Математическа верификация)
- Интеграция с двигатели за формална верификация (напр. **Batfish**).
- Логическа проверка на рутинг таблици и ACL политики без изпращане на реални пакети за пълно доказване на достъпността.

### 9.3 Event-Driven Closed-Loop Remediation
- Автоматично "самолечение" на мрежата: при засечено телеметрично събитие (напр. прекъсната сесия или влошено качество на връзката), платформата автоматично задейства предефинирани коригиращи действия.

### 9.4 Multi-Vendor Configuration Translation Engine (CLI Transpiler)
- Модул за автоматичен превод на конфигурационни блокове от един вендор към друг (напр. конвертиране на Cisco IOS OSPF/ACL настройки към Juniper JunOS или FortiOS синтаксис).

### 9.5 Out-of-Band (OOB) & Emergency Fallback
- Поддръжка на връзка през консолни сървъри (Opengear, Perle) през 4G/5G при пълен срив на основната мрежа за спешно възстановяване.

### 9.6 Green IT & ESG Energy Efficiency Optimization
- Мониторинг на консумацията на енергия (Watts) по PoE портове и захранващи модули.
- Автоматично планирано изключване на PoE захранването за аксес точки и IP телефони извън работно време за спестяване на енергия.

### 9.7 Autonomous AI Copilot & Root Cause Analysis (RCA)
- Автоматичен анализ на причинно-следствени връзки (Root Cause Analysis): съпоставяне на възникнал срив с конкретна промяна в конфигурациите от последните часове.
- Копилот с естествен език: генериране на проверени конфигурации и търсене в базата данни чрез чат.

### 9.8 Multi-tenancy & White-labeling
- Пълна изолация на данните между различни клиенти/отдели в една инсталация (критично за MSPs — Managed Service Providers).
- Персонализиране на брандинга (White-labeling).

### 9.9 Zero-Touch Provisioning (ZTP)
- Автоматично откриване и първоначално конфигуриране на чисто нови устройства при първото им включване в мрежата.

### 9.10 Custom Plugin System & Marketplace
- Публичен API и плъгин архитектура за общността и разработчици да създават нови vendor adapters, custom съобщения и репорти.

---

## 10. Препоръчителна матрица за приоритизация по фази

| Фаза | Цел | Модули |
|---|---|---|
| **Фаза 1 (MVP)** | Базов функционален NCM | 1.1 – 1.8 (Core & Sanitization), 6.1 (RBAC) |
| **Фаза 2** | Автоматизация и Сигурност | 3.1 – 3.6 (Automation & Guardrails), 6.2 – 6.3 (Audit & Vault), 4.1 (NETCONF) |
| **Фаза 3** | Разпределеност & Интеграции | 2.1 – 2.3 (Remote Collectors & PAM), 7.1 – 7.5 (APIs, SSOT & Integrations), 5.1 – 5.3 (Assets & EoX) |
| **Фаза 4** | Напреднал мониторинг & Cloud | 4.2 – 4.3 (Cloud & Certs), 8.1 – 8.4 (Observability, Topology & Digital Twin) |
| **Фаза 5 (Next-Gen)** | AIOps & Intent-Based Leader | 9.1 – 9.10 (IBN, Formal Verification, Closed-Loop, AI Copilot, Green IT) |

---
*Документът служи като пълна референтна архитектурна рамка за изграждане на съвременна софтуерна NCM платформа.*
