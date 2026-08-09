from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException
from typing import Optional, Dict, Any
import time
from app.models.device import Device, ConnectionProtocol, DeviceType


class DeviceConnectivityService:
    """Service for managing SSH/Telnet connections to network devices"""
    
    # Mapping of device types to Netmiko device types
    DEVICE_TYPE_MAPPING = {
        DeviceType.ROUTER: {
            'cisco': 'cisco_ios',
            'juniper': 'juniper_junos',
            'mikrotik': 'mikrotik_routeros',
            'hp': 'hp_procurve',
            'arista': 'arista_eos',
            'default': 'cisco_ios'
        },
        DeviceType.SWITCH: {
            'cisco': 'cisco_ios',
            'juniper': 'juniper_junos',
            'mikrotik': 'mikrotik_switch',
            'hp': 'hp_procurve',
            'arista': 'arista_eos',
            'default': 'cisco_ios'
        },
        DeviceType.FIREWALL: {
            'cisco': 'cisco_asa',
            'paloalto': 'paloalto_panos',
            'fortinet': 'fortinet',
            'checkpoint': 'checkpoint_gaia',
            'default': 'cisco_asa'
        },
        DeviceType.WIRELESS: {
            'cisco': 'cisco_wlc',
            'ubiquiti': 'ubiquiti_unifi',
            'default': 'cisco_wlc'
        },
        DeviceType.LOAD_BALANCER: {
            'f5': 'f5_ltm',
            'citrix': 'citrix_netscaler',
            'default': 'f5_ltm'
        },
        DeviceType.OTHER: {
            'default': 'cisco_ios'
        }
    }
    
    @staticmethod
    def get_netmiko_device_type(device: Device) -> str:
        """Determine Netmiko device type based on vendor and device type"""
        vendor_lower = device.vendor.lower() if device.vendor else ''
        device_type_mapping = DeviceConnectivityService.DEVICE_TYPE_MAPPING.get(
            device.device_type, 
            DeviceConnectivityService.DEVICE_TYPE_MAPPING[DeviceType.OTHER]
        )
        
        # Try to match vendor
        for vendor_key, netmiko_type in device_type_mapping.items():
            if vendor_key in vendor_lower:
                return netmiko_type
        
        # Return default for this device type
        return device_type_mapping.get('default', 'cisco_ios')
    
    @staticmethod
    def create_connection_params(device: Device) -> Dict[str, Any]:
        """Create connection parameters for Netmiko"""
        device_type = DeviceConnectivityService.get_netmiko_device_type(device)
        
        params = {
            'device_type': device_type,
            'host': device.ip_address,
            'port': device.port,
            'username': device.username,
            'password': device.password,
            'timeout': 30,
            'session_timeout': 60,
        }
        
        # Add enable password for Cisco-like devices
        if device.enable_password and 'cisco' in device_type:
            params['secret'] = device.enable_password
        
        # For Telnet
        if device.protocol == ConnectionProtocol.TELNET:
            params['device_type'] = device_type.replace('_ssh', '_telnet')
        
        return params
    
    @staticmethod
    def test_connection(device: Device) -> Dict[str, Any]:
        """Test connection to a device"""
        start_time = time.time()
        
        try:
            params = DeviceConnectivityService.create_connection_params(device)
            
            with ConnectHandler(**params) as connection:
                # Send a simple command to verify connection
                if 'cisco' in params['device_type']:
                    output = connection.send_command('show version', read_timeout=10)
                elif 'juniper' in params['device_type']:
                    output = connection.send_command('show version', read_timeout=10)
                elif 'mikrotik' in params['device_type']:
                    output = connection.send_command('/system resource print', read_timeout=10)
                else:
                    output = connection.send_command('show version', read_timeout=10)
                
                latency_ms = (time.time() - start_time) * 1000
                
                return {
                    'success': True,
                    'latency_ms': round(latency_ms, 2),
                    'error_message': None,
                    'output_sample': output[:500] if output else None
                }
                
        except NetmikoTimeoutException as e:
            return {
                'success': False,
                'latency_ms': None,
                'error_message': f'Connection timeout: {str(e)}',
                'output_sample': None
            }
        except NetmikoAuthenticationException as e:
            return {
                'success': False,
                'latency_ms': None,
                'error_message': f'Authentication failed: {str(e)}',
                'output_sample': None
            }
        except Exception as e:
            return {
                'success': False,
                'latency_ms': None,
                'error_message': f'Connection error: {str(e)}',
                'output_sample': None
            }
    
    @staticmethod
    def get_configuration(device: Device) -> Dict[str, Any]:
        """Retrieve configuration from a device"""
        try:
            params = DeviceConnectivityService.create_connection_params(device)
            
            with ConnectHandler(**params) as connection:
                # Enter enable mode if needed
                if 'cisco' in params['device_type'] and device.enable_password:
                    connection.enable()
                
                # Get configuration based on device type
                if 'cisco' in params['device_type']:
                    config = connection.send_command('show running-config', read_timeout=60)
                elif 'juniper' in params['device_type']:
                    config = connection.send_command('show configuration | display set', read_timeout=60)
                elif 'mikrotik' in params['device_type']:
                    config = connection.send_command('/export', read_timeout=60)
                elif 'hp' in params['device_type']:
                    config = connection.send_command('show running-config', read_timeout=60)
                elif 'arista' in params['device_type']:
                    config = connection.send_command('show running-config', read_timeout=60)
                else:
                    config = connection.send_command('show running-config', read_timeout=60)
                
                return {
                    'success': True,
                    'configuration': config,
                    'error_message': None
                }
                
        except NetmikoTimeoutException as e:
            return {
                'success': False,
                'configuration': None,
                'error_message': f'Connection timeout: {str(e)}'
            }
        except NetmikoAuthenticationException as e:
            return {
                'success': False,
                'configuration': None,
                'error_message': f'Authentication failed: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'configuration': None,
                'error_message': f'Error retrieving configuration: {str(e)}'
            }
    
    @staticmethod
    def send_command(device: Device, command: str, enable_mode: bool = False) -> Dict[str, Any]:
        """Send a command to a device and return the output"""
        try:
            params = DeviceConnectivityService.create_connection_params(device)
            
            with ConnectHandler(**params) as connection:
                # Enter enable mode if needed
                if enable_mode and 'cisco' in params['device_type'] and device.enable_password:
                    connection.enable()
                
                output = connection.send_command(command, read_timeout=60)
                
                return {
                    'success': True,
                    'output': output,
                    'error_message': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'output': None,
                'error_message': f'Error sending command: {str(e)}'
            }
    
    @staticmethod
    def send_config_commands(device: Device, commands: list) -> Dict[str, Any]:
        """Send configuration commands to a device"""
        try:
            params = DeviceConnectivityService.create_connection_params(device)
            
            with ConnectHandler(**params) as connection:
                # Enter config mode
                if 'cisco' in params['device_type'] and device.enable_password:
                    connection.enable()
                
                # Send configuration commands
                output = connection.send_config_set(commands, read_timeout=60)
                
                # Save configuration
                if 'cisco' in params['device_type']:
                    connection.save_config()
                elif 'juniper' in params['device_type']:
                    connection.send_command('commit', read_timeout=30)
                
                return {
                    'success': True,
                    'output': output,
                    'error_message': None
                }
                
        except Exception as e:
            return {
                'success': False,
                'output': None,
                'error_message': f'Error sending config commands: {str(e)}'
            }
