import re
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class ComplianceRule:
    """Represents a compliance rule"""
    name: str
    description: str
    severity: str  # critical, high, medium, low
    check_function: Callable[[str], Dict[str, Any]]
    category: str = "general"


@dataclass
class ComplianceResult:
    """Result of a compliance check"""
    rule_name: str
    status: ComplianceStatus
    message: str
    details: Optional[str] = None
    severity: str = "medium"
    line_number: Optional[int] = None


class ComplianceEngine:
    """Engine for checking configuration compliance against rules"""
    
    def __init__(self):
        self.rules = []
        self._load_default_rules()
    
    def _load_default_rules(self):
        """Load default compliance rules"""
        
        # Security rules
        self.add_rule(ComplianceRule(
            name="password_encryption",
            description="Ensure passwords are encrypted",
            severity="critical",
            check_function=self._check_password_encryption,
            category="security"
        ))
        
        self.add_rule(ComplianceRule(
            name="telnet_disabled",
            description="Ensure Telnet is disabled",
            severity="high",
            check_function=self._check_telnet_disabled,
            category="security"
        ))
        
        self.add_rule(ComplianceRule(
            name="ssh_enabled",
            description="Ensure SSH is enabled",
            severity="high",
            check_function=self._check_ssh_enabled,
            category="security"
        ))
        
        self.add_rule(ComplianceRule(
            name="acl_present",
            description="Ensure access control lists are configured",
            severity="medium",
            check_function=self._check_acl_present,
            category="security"
        ))
        
        # Network rules
        self.add_rule(ComplianceRule(
            name="ntp_configured",
            description="Ensure NTP is configured",
            severity="medium",
            check_function=self._check_ntp_configured,
            category="network"
        ))
        
        self.add_rule(ComplianceRule(
            name="logging_enabled",
            description="Ensure logging is enabled",
            severity="medium",
            check_function=self._check_logging_enabled,
            category="network"
        ))
        
        # Management rules
        self.add_rule(ComplianceRule(
            name="banner_configured",
            description="Ensure banner/motd is configured",
            severity="low",
            check_function=self._check_banner_configured,
            category="management"
        ))
        
        self.add_rule(ComplianceRule(
            name="description_present",
            description="Ensure interface descriptions are present",
            severity="low",
            check_function=self._check_description_present,
            category="management"
        ))
    
    def add_rule(self, rule: ComplianceRule):
        """Add a custom compliance rule"""
        self.rules.append(rule)
    
    def remove_rule(self, rule_name: str):
        """Remove a compliance rule by name"""
        self.rules = [r for r in self.rules if r.name != rule_name]
    
    def check_compliance(self, config: str, device_type: str = "cisco_ios") -> Dict[str, Any]:
        """Check configuration against all rules"""
        results = []
        
        for rule in self.rules:
            try:
                result = rule.check_function(config)
                results.append(ComplianceResult(
                    rule_name=rule.name,
                    status=result.get('status', ComplianceStatus.ERROR),
                    message=result.get('message', 'Check failed'),
                    details=result.get('details'),
                    severity=rule.severity,
                    line_number=result.get('line_number')
                ))
            except Exception as e:
                logger.error(f"Error checking rule {rule.name}: {str(e)}")
                results.append(ComplianceResult(
                    rule_name=rule.name,
                    status=ComplianceStatus.ERROR,
                    message=f"Check error: {str(e)}",
                    severity=rule.severity
                ))
        
        # Calculate overall compliance
        compliant_count = sum(1 for r in results if r.status == ComplianceStatus.COMPLIANT)
        total_count = len(results)
        compliance_percentage = (compliant_count / total_count * 100) if total_count > 0 else 0
        
        # Determine overall status
        critical_failures = sum(1 for r in results if r.severity == "critical" and r.status != ComplianceStatus.COMPLIANT)
        high_failures = sum(1 for r in results if r.severity == "high" and r.status != ComplianceStatus.COMPLIANT)
        
        if critical_failures > 0:
            overall_status = ComplianceStatus.NON_COMPLIANT
        elif high_failures > 0:
            overall_status = ComplianceStatus.WARNING
        elif compliance_percentage == 100:
            overall_status = ComplianceStatus.COMPLIANT
        else:
            overall_status = ComplianceStatus.WARNING
        
        return {
            'overall_status': overall_status,
            'compliance_percentage': round(compliance_percentage, 2),
            'total_rules': total_count,
            'compliant_rules': compliant_count,
            'non_compliant_rules': total_count - compliant_count,
            'results': results,
            'device_type': device_type
        }
    
    # Rule check functions
    
    def _check_password_encryption(self, config: str) -> Dict[str, Any]:
        """Check if passwords are encrypted"""
        if "service password-encryption" in config.lower():
            return {
                'status': ComplianceStatus.COMPLIANT,
                'message': 'Password encryption is enabled'
            }
        return {
            'status': ComplianceStatus.NON_COMPLIANT,
            'message': 'Password encryption is not enabled'
        }
    
    def _check_telnet_disabled(self, config: str) -> Dict[str, Any]:
        """Check if Telnet is disabled"""
        lines = config.lower().splitlines()
        telnet_lines = [line for line in lines if 'telnet' in line and 'transport input' in line]
        
        # Check if telnet is explicitly disabled or not allowed
        for line in telnet_lines:
            if 'transport input ssh' in line or 'no transport input telnet' in line:
                return {
                    'status': ComplianceStatus.COMPLIANT,
                    'message': 'Telnet is disabled'
                }
        
        return {
            'status': ComplianceStatus.NON_COMPLIANT,
            'message': 'Telnet may be enabled'
        }
    
    def _check_ssh_enabled(self, config: str) -> Dict[str, Any]:
        """Check if SSH is enabled"""
        if "ip ssh version 2" in config.lower() or "ip ssh" in config.lower():
            return {
                'status': ComplianceStatus.COMPLIANT,
                'message': 'SSH is enabled'
            }
        return {
            'status': ComplianceStatus.NON_COMPLIANT,
            'message': 'SSH is not enabled'
        }
    
    def _check_acl_present(self, config: str) -> Dict[str, Any]:
        """Check if access control lists are configured"""
        if re.search(r'ip access-list|access-list', config, re.IGNORECASE):
            return {
                'status': ComplianceStatus.COMPLIANT,
                'message': 'ACLs are configured'
            }
        return {
            'status': ComplianceStatus.WARNING,
            'message': 'No ACLs found'
        }
    
    def _check_ntp_configured(self, config: str) -> Dict[str, Any]:
        """Check if NTP is configured"""
        if re.search(r'ntp server|ntp source', config, re.IGNORECASE):
            return {
                'status': ComplianceStatus.COMPLIANT,
                'message': 'NTP is configured'
            }
        return {
            'status': ComplianceStatus.WARNING,
            'message': 'NTP is not configured'
        }
    
    def _check_logging_enabled(self, config: str) -> Dict[str, Any]:
        """Check if logging is enabled"""
        if re.search(r'logging\s+\d+\.\d+\.\d+\.\d+|logging host', config, re.IGNORECASE):
            return {
                'status': ComplianceStatus.COMPLIANT,
                'message': 'Logging is configured'
            }
        return {
            'status': ComplianceStatus.WARNING,
            'message': 'Remote logging is not configured'
        }
    
    def _check_banner_configured(self, config: str) -> Dict[str, Any]:
        """Check if banner/motd is configured"""
        if re.search(r'banner motd|banner login|banner exec', config, re.IGNORECASE):
            return {
                'status': ComplianceStatus.COMPLIANT,
                'message': 'Banner is configured'
            }
        return {
            'status': ComplianceStatus.WARNING,
            'message': 'Banner is not configured'
        }
    
    def _check_description_present(self, config: str) -> Dict[str, Any]:
        """Check if interface descriptions are present"""
        interface_lines = [line for line in config.splitlines() if 'interface' in line.lower()]
        description_lines = [line for line in config.splitlines() if 'description' in line.lower()]
        
        if len(description_lines) >= len(interface_lines) * 0.5:  # At least 50% have descriptions
            return {
                'status': ComplianceStatus.COMPLIANT,
                'message': f'Interface descriptions present ({len(description_lines)}/{len(interface_lines)})'
            }
        return {
            'status': ComplianceStatus.WARNING,
            'message': f'Missing interface descriptions ({len(description_lines)}/{len(interface_lines)})'
        }
    
    def add_custom_rule(
        self,
        name: str,
        description: str,
        severity: str,
        check_function: Callable[[str], Dict[str, Any]],
        category: str = "custom"
    ):
        """Add a custom compliance rule"""
        rule = ComplianceRule(
            name=name,
            description=description,
            severity=severity,
            check_function=check_function,
            category=category
        )
        self.add_rule(rule)
    
    def get_rules_by_category(self, category: str) -> List[ComplianceRule]:
        """Get all rules in a specific category"""
        return [r for r in self.rules if r.category == category]
    
    def get_all_categories(self) -> List[str]:
        """Get all rule categories"""
        categories = set(r.category for r in self.rules)
        return list(categories)
    
    def check_specific_rules(
        self,
        config: str,
        rule_names: List[str]
    ) -> Dict[str, Any]:
        """Check configuration against specific rules only"""
        results = []
        
        for rule in self.rules:
            if rule.name in rule_names:
                try:
                    result = rule.check_function(config)
                    results.append(ComplianceResult(
                        rule_name=rule.name,
                        status=result.get('status', ComplianceStatus.ERROR),
                        message=result.get('message', 'Check failed'),
                        details=result.get('details'),
                        severity=rule.severity,
                        line_number=result.get('line_number')
                    ))
                except Exception as e:
                    logger.error(f"Error checking rule {rule.name}: {str(e)}")
                    results.append(ComplianceResult(
                        rule_name=rule.name,
                        status=ComplianceStatus.ERROR,
                        message=f"Check error: {str(e)}",
                        severity=rule.severity
                    ))
        
        return {
            'total_rules_checked': len(results),
            'results': results
        }
