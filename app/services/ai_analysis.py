import re
from typing import List, Dict, Any


class AIAnalysisService:
    """
    AI-Assisted Configuration Analysis & Anomaly Detection Service (Module 6.1)

    Provides automated natural-language explanation of configuration diffs and
    executes statistical/structural anomaly detection across device backups.
    """

    @classmethod
    def explain_configuration_diff_ai(cls, diff_text: str) -> str:
        """
        Translates raw unified diffs into human-readable plain language (Bulgarian/English)
        to prevent unauthorized or dangerous leaks of access.
        """
        if not diff_text:
            return "Няма открити промени в конфигурацията за анализ."

        explanations = []
        lines = diff_text.splitlines()

        for line in lines:
            # 1. Interface shutdowns
            if line.startswith("+") and "shutdown" in line.lower() and "no shutdown" not in line.lower():
                explanations.append("• Мрежовият интерфейс е деактивиран (shutdown).")
            elif line.startswith("+") and "no shutdown" in line.lower():
                explanations.append("• Мрежовият интерфейс е активиран обратно в работен режим (no shutdown).")

            # 2. Open SSH/Telnet ports
            elif line.startswith("+") and "transport input telnet" in line.lower():
                explanations.append("• ВНИМАНИЕ: Активиран е несигурният протокол Telnet за отдалечен достъп!")
            elif line.startswith("+") and "transport input ssh" in line.lower():
                explanations.append("• Активиран е сигурният протокол SSH за отдалечен достъп.")

            # 3. Dynamic Routing adjustments
            elif line.startswith("+") and "router ospf" in line.lower():
                explanations.append("• Добавена е нова OSPF динамична маршрутизация на устройството.")
            elif line.startswith("+") and "router bgp" in line.lower():
                explanations.append("• Добавена е нова BGP динамична маршрутизация за връзка с автономна система.")

            # 4. Access lists (ACLs)
            elif line.startswith("+") and "permit" in line.lower() and "any" in line.lower() and "access-list" in line.lower():
                explanations.append("• ВНИМАНИЕ: Добавено е критично разрешително правило 'permit any', отварящо широк достъп!")

        if not explanations:
            return "Конфигурацията е претърпяла малки структурни или козметични промени, които не засягат директно мрежовата сигурност."

        summary_intro = "Анализ на мрежовите промени на естествен език (AI Copilot):\n"
        return summary_intro + "\n".join(explanations)

    @classmethod
    def detect_configuration_anomalies(cls, config_content: str) -> List[Dict[str, Any]]:
        """
        Scans backups using heuristic patterns and security guidelines
        to report high-risk configuration anomalies.
        """
        anomalies = []
        if not config_content:
            return anomalies

        # Anomaly 1: Plaintext community "public" or "private"
        if re.search(r"snmp-server\s+community\s+(public|private)", config_content, re.IGNORECASE):
            anomalies.append({
                "severity": "high",
                "category": "security",
                "message": "Използва се несигурно и стандартно SNMP комюнити име (public/private).",
                "remediation": "Променете комюнити низа с уникална сложна парола."
            })

        # Anomaly 2: Telnet enabled instead of SSH only
        if re.search(r"transport\s+input\s+.*telnet", config_content, re.IGNORECASE):
            anomalies.append({
                "severity": "medium",
                "category": "access_control",
                "message": "Активиран е некриптиран отдалечен достъп чрез Telnet.",
                "remediation": "Конфигурирайте 'transport input ssh' под vty линиите."
            })

        # Anomaly 3: No logging host configured
        if not re.search(r"logging\s+\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", config_content, re.IGNORECASE):
            anomalies.append({
                "severity": "low",
                "category": "compliance",
                "message": "Липсва отдалечен Syslog сървър за съхранение на логове.",
                "remediation": "Конфигурирайте 'logging <IP>' за централизиран одит."
            })

        return anomalies
