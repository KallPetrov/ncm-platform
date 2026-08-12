import re
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.device import Device, DeviceStatus, Configuration
from app.models.audit import AuditLog
from app.services.ai_analysis import AIAnalysisService


class AIAssistantService:
    """
    AI Assistant & Copilot Service for NCM Platform

    Processes natural language queries in Bulgarian, inspects the live database state,
    and returns contextual, real-world network operational intelligence, platform support Q&A,
    and step-by-step guides.
    """

    @classmethod
    def get_suggested_queries(cls) -> List[str]:
        """Returns standard suggestions for the UI."""
        return [
            "Колко устройства има в системата?",
            "Кои устройства са офлайн в момента?",
            "Има ли засичени сигурностни аномалии в конфигурациите?",
            "Как да конфигурирам OSPF маршрутизация на Cisco?",
            "Как да добавя ново устройство в платформата?",
            "Как работи ротацията на пароли и Secrets Vault?",
            "Как се прави бекъп на устройство?"
        ]

    @classmethod
    def process_chat_message(cls, db: Session, user_id: int, message: str) -> Dict[str, Any]:
        """
        Processes an incoming user message, parses its intent,
        queries the database dynamically, and generates a response in Bulgarian.
        """
        if not message:
            return {
                "response": "Моля, въведете въпрос за анализ.",
                "suggested_queries": cls.get_suggested_queries()
            }

        msg_lower = message.lower().strip()

        # 1. Intent: Specific Device Analysis (Priority 1: specific name or analysis)
        if "анализирай" in msg_lower or "анализ на" in msg_lower:
            return cls._handle_specific_device_analysis(db, message)

        # 2. Intent: Anomaly Detection / Security check across all devices (Priority 2)
        if any(keyword in msg_lower for keyword in ["аномал", "сканир", "провер", "заплах", "сигурнос"]):
            return cls._handle_all_anomalies(db)

        # 3. Intent: Offline Devices (Priority 3)
        if "офлайн" in msg_lower or "offline" in msg_lower:
            return cls._handle_offline_devices(db)

        # 4. Intent: Online Devices (Priority 4)
        if "онлайн" in msg_lower or "online" in msg_lower:
            return cls._handle_online_devices(db)

        # 5. Intent: Platform specific Q&A (Priority 5) - Checked before generic stats
        if any(keyword in msg_lower for keyword in ["как да добавя", "как се добавя", "как работи", "система", "ваулт", "vault", "бекъп", "backup", "терминал", "запис", "ротац", "netbox", "съответств", "compliance", "nis2", "logs"]):
            return cls._handle_platform_info(msg_lower)

        # 6. Intent: Device Count / System Stats (Priority 6)
        if any(keyword in msg_lower for keyword in ["колко", "устройств", "статистик", "инвентар"]):
            return cls._handle_system_stats(db)

        # 7. Intent: Latest Changes / Audit log (Priority 7)
        if any(keyword in msg_lower for keyword in ["одит", "хронолог", "промен", "активнос"]) or "кой е" in msg_lower or "кой направи" in msg_lower:
            return cls._handle_audit_logs(db)

        # 8. Intent: Config Guides / How-tos (Priority 8)
        if any(keyword in msg_lower for keyword in ["как да", "как се", "инструкц", "настроя"]):
            return cls._handle_config_guides(msg_lower)

        # Default Friendly Response (Fallback)
        response_text = (
            "Здравейте! Аз съм Вашият **AI Мрежов Асистент** (NCM Copilot) за платформата.\n\n"
            "Мога да Ви помогна с реална информация за мрежата Ви, както и с инструкции за използването на самата платформа! Ето няколко теми:\n"
            "• **Управление на инвентара**: Напишете *'Как да добавя ново устройство?'*\n"
            "• **Ротация на пароли**: Напишете *'Как работи Secrets Vault?'*\n"
            "• **Бекъп архиви**: Напишете *'Как се прави бекъп на устройство?'*\n"
            "• **Уеб Терминал & Одит**: Напишете *'Как се записва SSH сесия?'*\n"
            "• **NetBox SSOT Синхронизация**: Напишете *'Как се синхронизира с NetBox?'*\n"
            "• **Засичане на аномалии**: Напишете *'Има ли засичени аномалии?'*\n\n"
            "Какво бихте искали да разберете в момента?"
        )

        return {
            "response": response_text,
            "suggested_queries": cls.get_suggested_queries()
        }

    @classmethod
    def _handle_system_stats(cls, db: Session) -> Dict[str, Any]:
        devices = db.query(Device).all()
        total = len(devices)
        if total == 0:
            return {
                "response": "В момента в платформата **няма регистрирани устройства**. Можете да добавите устройство от панела 'Devices'.",
                "suggested_queries": cls.get_suggested_queries()
            }

        online = sum(1 for d in devices if d.status == DeviceStatus.ONLINE)
        offline = sum(1 for d in devices if d.status == DeviceStatus.OFFLINE)
        maintenance = sum(1 for d in devices if d.status == DeviceStatus.MAINTENANCE)
        unknown = sum(1 for d in devices if d.status == DeviceStatus.UNKNOWN)

        vendors = {}
        for d in devices:
            v = d.vendor or "Unknown"
            vendors[v] = vendors.get(v, 0) + 1

        vendor_summary = ", ".join([f"{v}: {count}" for v, count in vendors.items()])

        response_text = (
            f"### 📊 Текуща статистика на мрежовия инвентар:\n"
            f"• **Общ брой устройства**: {total}\n"
            f"• 🟢 **Онлайн**: {online}\n"
            f"• 🔴 **Офлайн**: {offline}\n"
            f"• 🟡 **Поддръжка (Maintenance)**: {maintenance}\n"
            f"• ⚪ **Неизвестно състояние**: {unknown}\n\n"
            f"**Разпределение по производители (Vendors):**\n"
            f"{vendor_summary}\n\n"
            f"Всички данни са напълно реални и извлечени от базата данни в този момент!"
        )

        return {
            "response": response_text,
            "suggested_queries": cls.get_suggested_queries()
        }

    @classmethod
    def _handle_offline_devices(cls, db: Session) -> Dict[str, Any]:
        offline_devices = db.query(Device).filter(Device.status == DeviceStatus.OFFLINE).all()
        if not offline_devices:
            return {
                "response": "🎉 Страхотна новина! **Няма офлайн устройства** в системата. Всички устройства работят нормално или са в неизвестно състояние.",
                "suggested_queries": cls.get_suggested_queries()
            }

        dev_list = []
        for i, d in enumerate(offline_devices, start=1):
            last_seen_str = d.last_seen.strftime('%Y-%m-%d %H:%M:%S') if d.last_seen else "никога"
            dev_list.append(f"{i}. **{d.name}** ({d.ip_address}) - Vendor: {d.vendor or 'Unknown'}, Последно видян: {last_seen_str}")

        response_text = (
            f"### 🔴 Списък на офлайн мрежовите устройства ({len(offline_devices)}):\n"
            + "\n".join(dev_list)
            + "\n\nПрепоръчва се проверка на физическата свързаност или SSH/Telnet портовете на тези устройства."
        )

        return {
            "response": response_text,
            "suggested_queries": cls.get_suggested_queries()
        }

    @classmethod
    def _handle_online_devices(cls, db: Session) -> Dict[str, Any]:
        online_devices = db.query(Device).filter(Device.status == DeviceStatus.ONLINE).all()
        if not online_devices:
            return {
                "response": "⚠️ Няма засичени **онлайн устройства** в базата данни в момента. Проверете връзките или стартирайте Connection Test.",
                "suggested_queries": cls.get_suggested_queries()
            }

        dev_list = []
        for i, d in enumerate(online_devices, start=1):
            dev_list.append(f"{i}. **{d.name}** ({d.ip_address}) - {d.vendor or 'Unknown'} {d.model or ''}")

        response_text = (
            f"### 🟢 Списък на онлайн устройствата ({len(online_devices)}):\n"
            + "\n".join(dev_list)
        )

        return {
            "response": response_text,
            "suggested_queries": cls.get_suggested_queries()
        }

    @classmethod
    def _handle_all_anomalies(cls, db: Session) -> Dict[str, Any]:
        devices = db.query(Device).all()
        all_anomalies = []

        for d in devices:
            latest_conf = db.query(Configuration).filter(
                Configuration.device_id == d.id
            ).order_by(Configuration.version.desc()).first()

            if latest_conf and latest_conf.content:
                anoms = AIAnalysisService.detect_configuration_anomalies(latest_conf.content)
                for an in anoms:
                    all_anomalies.append({
                        "device_name": d.name,
                        "device_ip": d.ip_address,
                        **an
                    })

        if not all_anomalies:
            return {
                "response": "✅ **Няма намерени критични аномалии** в текущите конфигурации на Вашите устройства! Всички сканирани правила за сигурност са в съответствие.",
                "suggested_queries": cls.get_suggested_queries()
            }

        response_text = "### ⚠️ Открити аномалии и заплахи за сигурността:\n\n"
        for i, an in enumerate(all_anomalies, start=1):
            severity_icon = "🔴" if an["severity"] == "high" else "🟡" if an["severity"] == "medium" else "🔵"
            response_text += (
                f"{i}. {severity_icon} **[{an['severity'].upper()}]** на устройство **{an['device_name']}** ({an['device_ip']}):\n"
                f"   - **Категория**: {an['category']}\n"
                f"   - **Проблем**: {an['message']}\n"
                f"   - **Решение**: {an['remediation']}\n\n"
            )

        response_text += "\nПрепоръчително е да предприете коригиращи действия по сигурността възможно най-скоро."
        return {
            "response": response_text,
            "suggested_queries": cls.get_suggested_queries()
        }

    @classmethod
    def _handle_specific_device_analysis(cls, db: Session, message: str) -> Dict[str, Any]:
        # Extract potential device name from message
        words = message.split()
        device_name = ""
        for word in words:
            if word.lower() not in ["анализирай", "устройство", "анализ", "на", "ми"]:
                device_name = word.strip("?,.!")
                break

        if not device_name:
            # Let's list some registered devices so they can select one
            all_devices = db.query(Device).limit(5).all()
            if not all_devices:
                return {
                    "response": "Няма регистрирани устройства, които да анализирам.",
                    "suggested_queries": cls.get_suggested_queries()
                }
            dev_names = ", ".join([f"'{d.name}'" for d in all_devices])
            return {
                "response": f"Моля, посочете името на устройството, което искате да анализирам. Налични устройства: {dev_names}.\n\nПример: *'Анализирай устройство {all_devices[0].name}'*",
                "suggested_queries": [f"Анализирай устройство {d.name}" for d in all_devices]
            }

        # Query device by name
        device = db.query(Device).filter(Device.name.ilike(f"%{device_name}%")).first()
        if not device:
            return {
                "response": f"❌ Устройство с име **'{device_name}'** не беше намерено в базата данни на платформата.",
                "suggested_queries": cls.get_suggested_queries()
            }

        # Get latest configuration
        latest_conf = db.query(Configuration).filter(
            Configuration.device_id == device.id
        ).order_by(Configuration.version.desc()).first()

        if not latest_conf or not latest_conf.content:
            return {
                "response": f"⚠️ За устройство **'{device.name}'** ({device.ip_address}) няма запазени конфигурации в системата, за да извърша анализ.",
                "suggested_queries": cls.get_suggested_queries()
            }

        anomalies = AIAnalysisService.detect_configuration_anomalies(latest_conf.content)
        anomalies_summary = ""
        if not anomalies:
            anomalies_summary = "🟢 Няма засичени аномалии по сигурността в конфигурацията!"
        else:
            anomalies_summary = "⚠️ **Открити проблеми по сигурността:**\n"
            for an in anomalies:
                severity_icon = "🔴" if an["severity"] == "high" else "🟡" if an["severity"] == "medium" else "🔵"
                anomalies_summary += f" - {severity_icon} *[{an['severity'].upper()}]* {an['message']} (Препоръка: {an['remediation']})\n"

        response_text = (
            f"### 🔍 Детайлен анализ на устройство **{device.name}**:\n"
            f"• **IP адрес**: {device.ip_address}\n"
            f"• **Тип**: {device.device_type.value if getattr(device.device_type, 'value', None) else str(device.device_type)}\n"
            f"• **Производител**: {device.vendor or 'Unknown'}\n"
            f"• **Текуща версия**: {device.model or 'Unknown'}\n"
            f"• **Последен архив**: {device.last_backup.strftime('%Y-%m-%d %H:%M:%S') if device.last_backup else 'никога'}\n"
            f"• **Размер на конфиг**: {len(latest_conf.content)} символа\n\n"
            f"#### 🛡️ Анализ за сигурност:\n"
            f"{anomalies_summary}\n\n"
            f"Мога също да изведа текстови diff на последната промяна на това устройство!"
        )

        return {
            "response": response_text,
            "suggested_queries": cls.get_suggested_queries()
        }

    @classmethod
    def _handle_audit_logs(cls, db: Session) -> Dict[str, Any]:
        logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(5).all()
        if not logs:
            return {
                "response": "В системата все още няма записани системни одитни събития.",
                "suggested_queries": cls.get_suggested_queries()
            }

        log_list = []
        for l in logs:
            ts = l.created_at.strftime('%Y-%m-%d %H:%M:%S')
            user_str = l.username if l.username else "System"
            log_list.append(f"• `[{ts}]` **{user_str}** извърши действие **'{l.action}'** върху **{l.resource_type}** (ID: {l.resource_id}). Подробности: {l.details or 'няма'}")

        response_text = (
            "### 📑 Хронология на последните 5 системни промени (Одитен дневник):\n"
            + "\n".join(log_list)
            + "\n\nОдитният дневник е защитен срещу изтриване и отговаря на NIS2 изискванията за прозрачност!"
        )

        return {
            "response": response_text,
            "suggested_queries": cls.get_suggested_queries()
        }

    @classmethod
    def _handle_config_guides(cls, msg_lower: str) -> Dict[str, Any]:
        # Detect topic
        if "ospf" in msg_lower:
            response_text = (
                "### 🗺️ Инструкция за конфигуриране на OSPF (Cisco IOS):\n\n"
                "За да активирате OSPF динамично рутиране на Cisco рутер, използвайте следните CLI команди:\n"
                "```config\n"
                "router ospf 1\n"
                " network 192.168.1.0 0.0.0.255 area 0\n"
                " network 10.0.0.0 0.0.0.3 area 0\n"
                " log-adjacency-changes\n"
                " exit\n"
                "```\n"
                "**Обяснение:**\n"
                "1. `router ospf 1` стартира OSPF процеса с ID 1.\n"
                "2. `network <subnet> <wildcard-mask> area <area-id>` указва на кои интерфейси да се активира OSPF и коя област (Area) да принадлежат."
            )
        elif "bgp" in msg_lower:
            response_text = (
                "### 🌐 Инструкция за конфигуриране на BGP (Cisco IOS):\n\n"
                "Базова конфигурация на BGP за връзка със съсед (Peer):\n"
                "```config\n"
                "router bgp 65001\n"
                " neighbor 192.0.2.1 remote-as 65002\n"
                " neighbor 192.0.2.1 description Peer-to-ISP\n"
                " address-family ipv4 unicast\n"
                "  neighbor 192.0.2.1 activate\n"
                "  network 203.0.113.0 mask 255.255.255.0\n"
                "  exit-address-family\n"
                "```\n"
                "BGP изисква точно дефиниране на автономните системи (AS) и активиране на адресните фамилии."
            )
        elif "ssh" in msg_lower:
            response_text = (
                "### 🔐 Инструкция за активиране на сигурен SSH достъп (Cisco IOS):\n\n"
                "Заменете несигурния Telnet с криптиран SSH достъп чрез следните стъпки:\n"
                "```config\n"
                "hostname Router-Edge\n"
                "ip domain-name company.local\n"
                "crypto key generate rsa general-keys modulus 2048\n"
                "ip ssh version 2\n"
                "username admin privilege 15 secret ComplexPassword123!\n"
                "line vty 0 4\n"
                " login local\n"
                " transport input ssh\n"
                " exit\n"
                "```\n"
                "**Внимание:** Наличието на `transport input ssh` забранява Telnet и принуждава използването само на SSH."
            )
        elif "vlan" in msg_lower:
            response_text = (
                "### 🔌 Инструкция за конфигуриране на VLAN-и (Cisco IOS Switch):\n\n"
                "Дефиниране на локална мрежа и задаване на порт към нея:\n"
                "```config\n"
                "vlan 10\n"
                " name Users-LAN\n"
                "exit\n"
                "interface GigabitEthernet0/5\n"
                " switchport mode access\n"
                " switchport access vlan 10\n"
                " spanning-tree portfast\n"
                " exit\n"
                "```\n"
                "Вторият блок конфигурира порта като `access` порт и го причислява към новия VLAN 10."
            )
        else:
            response_text = (
                "### 🔧 Наръчник за мрежови конфигурации:\n\n"
                "Мога да генерирам конфигурационни шаблони за:\n"
                "• **OSPF** (напишете *'Как се конфигурира OSPF?'*)\n"
                "• **BGP** (напишете *'Как се конфигурира BGP?'*)\n"
                "• **SSH** (напишете *'Как се пуска SSH?'*)\n"
                "• **VLAN** (напишете *'Как се добавя VLAN?'*)\n\n"
                "Посочете конкретен протокол за пълни CLI команди!"
            )

        return {
            "response": response_text,
            "suggested_queries": cls.get_suggested_queries()
        }

    @classmethod
    def _handle_platform_info(cls, msg_lower: str) -> Dict[str, Any]:
        """Provides highly detailed interactive guides on platform-specific features."""
        # 1. Topic: Adding Devices
        if "добавя" in msg_lower or "device" in msg_lower:
            response_text = (
                "### ➕ Ръководство за добавяне на ново устройство в NCM:\n\n"
                "За да регистрирате и започнете управление на устройство, изпълнете следните стъпки:\n"
                "1. Отидете в панела **Devices** от страничното меню.\n"
                "2. Кликнете на бутона **+ Add Device** горе вдясно.\n"
                "3. Попълнете следните полета в отворилия се диалог:\n"
                "   - **Name**: Уникално име за идентификация (напр. `Sofia-Switch-01`)\n"
                "   - **IP Address**: Валиден IP адрес или хост име\n"
                "   - **Device Type**: Изберете дали е `router`, `switch`, `firewall`, `wireless` и др.\n"
                "   - **Vendor**: Изберете производител (`Cisco`, `Juniper`, `MikroTik`, `HP`, `Arista`)\n"
                "   - **Connection Settings**: Изберете `SSH` или `Telnet` протокол, порт и въведете административни потребителско име и пароли.\n"
                "4. Кликнете **Save**, за да запишете промените.\n\n"
                "**Сигурност:** Вашите пароли се криптират динамично at-rest с AES-256 (Fernet) в базата ни данни."
            )
        # 2. Topic: Backup
        elif "бекъп" in msg_lower or "backup" in msg_lower:
            response_text = (
                "### 💾 Ръководство за Бекъпи и Архивиране на Конфигурации:\n\n"
                "Платформата поддържа както автоматично, така и ръчно сваляне на резервни копия на конфигурациите:\n"
                "• **Ръчен Бекъп**: В панела 'Devices', кликнете върху иконата за облак ☁️ срещу съответното устройство. Това веднага задейства задача за изтегляне.\n"
                "• **Автоматичен Бекъп**: Настройва се чрез `backup_interval` (в секунди) на ниво устройство. Бекъп мениджърът периодично проверява и сваля конфигурациите.\n"
                "• **Git Версиониране**: Всеки свален архив преминава през засичане на разлики. Ако има промяна, конфигурацията автоматично се добавя като нов коммит в Git репозиторито ни (`./storage/configs`), позволявайки детайлно проследяване на diff хронологията.\n"
                "• **Изтриване на Тайни данни**: Преди съхранение в базата или Git, конфигурацията минава през автоматичен Sanitization Engine, маскиращ пароли, SNMP комюнитита, private keys и др."
            )
        # 3. Topic: Terminal / SSH
        elif "терминал" in msg_lower or "ssh" in msg_lower or "запис" in msg_lower:
            response_text = (
                "### 🖥️ Уеб Терминал (Web SSH) & Session Recording (PAM Proxy):\n\n"
                "Нашата платформа включва вграден уеб-базиран терминал, който е сертифициран по изискванията на NIS2:\n"
                "• **PAM Proxy (Privileged Access Management)**: Инженерите могат да отворят директна SSH сесия към устройство през браузъра, без реално да виждат или въвеждат паролата му. Платформата инжектира паролата автоматично от криптирания сейф.\n"
                "• **Записване на сесии (Keystroke Logging)**: Всяка натисната клавишна комбинация, въведена команда и върнат отговор се записват в защитена база данни.\n"
                "• **NIS2 Съответствие**: Само потребители с роля `admin` или `auditor` могат да преглеждат пълната одитна следа на терминалните сесии, за да се гарантира абсолютна проследимост при инциденти."
            )
        # 4. Topic: Secrets Vault / Rotation
        elif "ротац" in msg_lower or "парол" in msg_lower or "vault" in msg_lower:
            response_text = (
                "### 🔑 Secrets Vault & Автоматизирана Ротация на Пароли:\n\n"
                "Платформата разполага със собствена защитена среда за управление на пароли и тайни ключове:\n"
                "• **Fernet Криптиране**: Всички пароли за устройствата и `enable` пароли се шифроват симетрично с алгоритъм AES-256 в режим Fernet. Ключът за декриптиране се генерира динамично от вашия `SECRET_KEY` и никога не се излага в чист вид.\n"
                "• **Автоматична ротация**: `SecretsVaultService` поддържа автоматична смяна на административните пароли. Платформата се свързва към устройството, изпълнява необходимите CLI команди за актуализиране на локалния потребител, и след това записва новата парола криптирана в Vault-а.\n"
                "• **Одитно логване**: Всяка смяна на парола задейства незабавно одитна запис за архивиране."
            )
        # 5. Topic: NetBox Sync
        elif "netbox" in msg_lower or "nautobot" in msg_lower or "синхрон" in msg_lower:
            response_text = (
                "### 🔄 Двупосочна Синхронизация с NetBox / Nautobot SSOT:\n\n"
                "Платформата се интегрира безпроблемно с външни бази Single Source of Truth (SSOT):\n"
                "• **Импорт от NetBox**: Нашят `SSOTSyncService` се свързва с Вашия NetBox API, изтегля регистрираните устройства в DCIM и автоматично ги добавя в NCM, разпознавайки IP адреси, производители (Vendors), сайтове (Sites) и роли.\n"
                "• **Експорт обратно**: NCM може да изпраща автоматично мрежови данни (напр. дата на последен бекъп, открит фърмуер / OS версия) обратно към NetBox за обогатяване на инвентара.\n"
                "• **Управление**: Настройва се от системния панел за настройки, където се въвеждат URL на NetBox и Token."
            )
        # 6. Topic: Compliance / Съответствие
        elif "съответств" in msg_lower or "compliance" in msg_lower or "правила" in msg_lower:
            response_text = (
                "### 🛡️ Compliance Engine & Проверка на Правила за Сигурност:\n\n"
                "Модулът за съответствие проверява автоматично дали Вашите мрежови конфигурации отговарят на дефинирани правила:\n"
                "• **Правила за анализ**: Вградените правила проверяват за активиран Telnet, несигурни SNMP communities (public/private), липса на Syslog сървър или NTP конфигурации.\n"
                "• **Автоматични доклади**: При всяка промяна на конфигурацията, `ComplianceEngine` сканира съдържанието и изчислява общ процент на съответствие (напр. 85% съвместимост) и списък с нарушения (Violations).\n"
                "• **Интеграция с UI**: В таб 'Compliance Reports' инженерите виждат графично обобщение по устройства и сектори за бърз анализ."
            )
        # 7. Topic: Audit / NIS2 / Logs
        elif "одит" in msg_lower or "дневник" in msg_lower or "nis2" in msg_lower or "logs" in msg_lower:
            response_text = (
                "### 📑 Immutable Audit Logs (Одит по стандарта NIS2 / ISO 27001):\n"
                "Всички административни и операционни действия на потребителите в платформата се логват неизтриваемо:\n"
                "• **Неизтриваемост (Immutable logs)**: Веднъж записан, одитният запис не може да се редактира или изтрива през API-то или интерфейса.\n"
                "• **NIS2 съвместимост**: Системата логва: Кой е извършил промяната (username), от кое IP, кога (точно време) и какво е засягало действието.\n"
                "• **Преглед**: Одитните логове са достъпни само за администратори през таб 'Audit Logs', където могат да се филтрират по действие и потребител."
            )
        else:
            response_text = (
                "### 📘 Информация за NCM Платформата:\n\n"
                "Мога да Ви разкажа подробно за всяка една от следните теми:\n"
                "1. **Добавяне на ново устройство** (напишете *'Как се добавя устройство?'*)\n"
                "2. **Конфигурационни Бекъпи** (напишете *'Разкажи ми за бекъпите'*)\n"
                "3. **Secrets Vault & Ротация** (напишете *'Как работи ротацията на пароли?'*)\n"
                "4. **Web SSH Терминал** (напишете *'Как работи уеб терминала?'*)\n"
                "5. **NetBox Синхронизация** (напишете *'Как се синхронизира с NetBox?'*)\n"
                "6. **Compliance & Сигурност** (напишете *'Как работи Compliance Engine?'*)\n"
                "7. **Одит и NIS2** (напишете *'Разкажи ми за одитните логове'*)\n\n"
                "Напишете някоя от ключовите думи за подробен наръчник!"
            )

        return {
            "response": response_text,
            "suggested_queries": cls.get_suggested_queries()
        }
