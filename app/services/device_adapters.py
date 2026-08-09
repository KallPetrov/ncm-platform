from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.models.device import Device


class DeviceAdapter(ABC):
    """Abstract base class for device adapters"""
    
    @abstractmethod
    def get_backup_command(self) -> str:
        """Get the command to retrieve configuration"""
        pass
    
    @abstractmethod
    def get_save_command(self) -> str:
        """Get the command to save configuration"""
        pass
    
    @abstractmethod
    def get_enable_mode_command(self) -> str:
        """Get the command to enter enable mode"""
        pass
    
    @abstractmethod
    def get_config_mode_command(self) -> str:
        """Get the command to enter configuration mode"""
        pass
    
    @abstractmethod
    def get_exit_config_mode_command(self) -> str:
        """Get the command to exit configuration mode"""
        pass
    
    @abstractmethod
    def normalize_config(self, config: str) -> str:
        """Normalize configuration for comparison"""
        pass
    
    @abstractmethod
    def get_netmiko_device_type(self) -> str:
        """Get Netmiko device type"""
        pass


class CiscoIOSAdapter(DeviceAdapter):
    """Adapter for Cisco IOS devices"""
    
    def get_backup_command(self) -> str:
        return "show running-config"
    
    def get_save_command(self) -> str:
        return "write memory"
    
    def get_enable_mode_command(self) -> str:
        return "enable"
    
    def get_config_mode_command(self) -> str:
        return "configure terminal"
    
    def get_exit_config_mode_command(self) -> str:
        return "end"
    
    def normalize_config(self, config: str) -> str:
        # Remove timestamps and dynamic data
        lines = []
        for line in config.splitlines():
            # Skip lines with timestamps
            if "Last configuration change" in line:
                continue
            if "NVRAM config last updated" in line:
                continue
            lines.append(line)
        return "\n".join(lines)
    
    def get_netmiko_device_type(self) -> str:
        return "cisco_ios"
    
    def get_pre_backup_commands(self) -> List[str]:
        return ["terminal length 0", "terminal width 0"]
    
    def get_post_backup_commands(self) -> List[str]:
        return ["terminal length 24", "terminal width 80"]


class CiscoASAAdapter(DeviceAdapter):
    """Adapter for Cisco ASA devices"""
    
    def get_backup_command(self) -> str:
        return "show running-config"
    
    def get_save_command(self) -> str:
        return "write memory"
    
    def get_enable_mode_command(self) -> str:
        return "enable"
    
    def get_config_mode_command(self) -> str:
        return "configure terminal"
    
    def get_exit_config_mode_command(self) -> str:
        return "end"
    
    def normalize_config(self, config: str) -> str:
        lines = []
        for line in config.splitlines():
            if "ASA Version" in line:
                continue
            if "Serial Number" in line:
                continue
            lines.append(line)
        return "\n".join(lines)
    
    def get_netmiko_device_type(self) -> str:
        return "cisco_asa"


class MikroTikAdapter(DeviceAdapter):
    """Adapter for MikroTik RouterOS devices"""
    
    def get_backup_command(self) -> str:
        return "/export"
    
    def get_save_command(self) -> str:
        return "/file save"
    
    def get_enable_mode_command(self) -> str:
        return ""  # MikroTik doesn't have enable mode
    
    def get_config_mode_command(self) -> str:
        return ""  # MikroTik doesn't have separate config mode
    
    def get_exit_config_mode_command(self) -> str:
        return ""  # MikroTik doesn't have separate config mode
    
    def normalize_config(self, config: str) -> str:
        # MikroTik export is already normalized
        return config
    
    def get_netmiko_device_type(self) -> str:
        return "mikrotik_routeros"


class JuniperJunosAdapter(DeviceAdapter):
    """Adapter for Juniper JunOS devices"""
    
    def get_backup_command(self) -> str:
        return "show configuration | display set"
    
    def get_save_command(self) -> str:
        return "commit"
    
    def get_enable_mode_command(self) -> str:
        return ""  # JunOS doesn't have enable mode
    
    def get_config_mode_command(self) -> str:
        return "configure"
    
    def get_exit_config_mode_command(self) -> str:
        return "exit"
    
    def normalize_config(self, config: str) -> str:
        lines = []
        for line in config.splitlines():
            if "last commit" in line:
                continue
            lines.append(line)
        return "\n".join(lines)
    
    def get_netmiko_device_type(self) -> str:
        return "juniper_junos"


class HPProCurveAdapter(DeviceAdapter):
    """Adapter for HP ProCurve devices"""
    
    def get_backup_command(self) -> str:
        return "show running-config"
    
    def get_save_command(self) -> str:
        return "write memory"
    
    def get_enable_mode_command(self) -> str:
        return ""  # HP ProCurve doesn't have enable mode
    
    def get_config_mode_command(self) -> str:
        return "configure"
    
    def get_exit_config_mode_command(self) -> str:
        return "end"
    
    def normalize_config(self, config: str) -> str:
        lines = []
        for line in config.splitlines():
            if "System Name" in line:
                continue
            lines.append(line)
        return "\n".join(lines)
    
    def get_netmiko_device_type(self) -> str:
        return "hp_procurve"


class AristaEOSAdapter(DeviceAdapter):
    """Adapter for Arista EOS devices"""
    
    def get_backup_command(self) -> str:
        return "show running-config"
    
    def get_save_command(self) -> str:
        return "write memory"
    
    def get_enable_mode_command(self) -> str:
        return "enable"
    
    def get_config_mode_command(self) -> str:
        return "configure terminal"
    
    def get_exit_config_mode_command(self) -> str:
        return "end"
    
    def normalize_config(self, config: str) -> str:
        lines = []
        for line in config.splitlines():
            if "Last configuration change" in line:
                continue
            lines.append(line)
        return "\n".join(lines)
    
    def get_netmiko_device_type(self) -> str:
        return "arista_eos"


class DeviceAdapterFactory:
    """Factory for creating device adapters"""
    
    _adapters = {
        'cisco': CiscoIOSAdapter,
        'cisco_ios': CiscoIOSAdapter,
        'cisco_asa': CiscoASAAdapter,
        'mikrotik': MikroTikAdapter,
        'mikrotik_routeros': MikroTikAdapter,
        'juniper': JuniperJunosAdapter,
        'juniper_junos': JuniperJunosAdapter,
        'hp': HPProCurveAdapter,
        'hp_procurve': HPProCurveAdapter,
        'arista': AristaEOSAdapter,
        'arista_eos': AristaEOSAdapter,
    }
    
    @classmethod
    def get_adapter(cls, device: Device) -> DeviceAdapter:
        """Get the appropriate adapter for a device"""
        vendor_lower = device.vendor.lower() if device.vendor else ''
        
        # Try to match vendor
        for vendor_key, adapter_class in cls._adapters.items():
            if vendor_key in vendor_lower:
                return adapter_class()
        
        # Default to Cisco IOS
        return CiscoIOSAdapter()
    
    @classmethod
    def get_adapter_by_vendor(cls, vendor: str) -> DeviceAdapter:
        """Get adapter by vendor name"""
        vendor_lower = vendor.lower()
        
        for vendor_key, adapter_class in cls._adapters.items():
            if vendor_key in vendor_lower:
                return adapter_class()
        
        return CiscoIOSAdapter()
    
    @classmethod
    def register_adapter(cls, vendor: str, adapter_class: type):
        """Register a custom adapter for a vendor"""
        cls._adapters[vendor.lower()] = adapter_class
    
    @classmethod
    def get_supported_vendors(cls) -> List[str]:
        """Get list of supported vendors"""
        return list(cls._adapters.keys())
