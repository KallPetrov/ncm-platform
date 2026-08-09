from jinja2 import Template, Environment, BaseLoader
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.device import Device
from app.services.device_connectivity import DeviceConnectivityService
from app.services.device_adapters import DeviceAdapterFactory
import logging

logger = logging.getLogger(__name__)


class AutomationService:
    """Service for bulk network automation using Jinja2 templates"""
    
    def __init__(self):
        self.env = Environment(loader=BaseLoader())
    
    def render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Render a Jinja2 template with variables"""
        try:
            template_obj = self.env.from_string(template)
            return template_obj.render(**variables)
        except Exception as e:
            logger.error(f"Template rendering failed: {str(e)}")
            raise
    
    def apply_config_to_device(
        self,
        device: Device,
        config_commands: List[str],
        save_config: bool = True
    ) -> Dict[str, Any]:
        """Apply configuration commands to a single device"""
        try:
            adapter = DeviceAdapterFactory.get_adapter(device)
            
            # Use device connectivity service to send commands
            result = DeviceConnectivityService.send_config_commands(
                device, config_commands
            )
            
            if result['success']:
                logger.info(f"Successfully applied config to device {device.name}")
            else:
                logger.error(f"Failed to apply config to device {device.name}: {result['error_message']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error applying config to device {device.name}: {str(e)}")
            return {
                'success': False,
                'output': None,
                'error_message': str(e)
            }
    
    def apply_template_to_devices(
        self,
        devices: List[Device],
        template: str,
        variables: Dict[str, Any],
        save_config: bool = True
    ) -> List[Dict[str, Any]]:
        """Apply a template to multiple devices"""
        results = []
        
        for device in devices:
            try:
                # Prepare device-specific variables
                device_vars = {
                    **variables,
                    'device_name': device.name,
                    'device_ip': device.ip_address,
                    'device_vendor': device.vendor or 'unknown',
                    'device_model': device.model or 'unknown',
                }
                
                # Render template for this device
                rendered_config = self.render_template(template, device_vars)
                
                # Parse rendered config into commands
                commands = self._parse_config_commands(rendered_config)
                
                # Apply to device
                result = self.apply_config_to_device(device, commands, save_config)
                
                results.append({
                    'device_id': device.id,
                    'device_name': device.name,
                    'device_ip': device.ip_address,
                    'success': result['success'],
                    'error_message': result.get('error_message'),
                    'output': result.get('output')
                })
                
            except Exception as e:
                logger.error(f"Error processing device {device.name}: {str(e)}")
                results.append({
                    'device_id': device.id,
                    'device_name': device.name,
                    'device_ip': device.ip_address,
                    'success': False,
                    'error_message': str(e),
                    'output': None
                })
        
        return results
    
    def _parse_config_commands(self, config: str) -> List[str]:
        """Parse configuration text into individual commands"""
        # Split by newlines and filter empty lines
        commands = [line.strip() for line in config.splitlines() if line.strip()]
        
        # Remove comment lines (starting with ! or #)
        commands = [cmd for cmd in commands if not cmd.startswith('!') and not cmd.startswith('#')]
        
        return commands
    
    def apply_bulk_config(
        self,
        device_ids: List[int],
        config_commands: List[str],
        db: Session,
        save_config: bool = True
    ) -> Dict[str, Any]:
        """Apply configuration commands to multiple devices by ID"""
        devices = db.query(Device).filter(Device.id.in_(device_ids)).all()
        
        if not devices:
            return {
                'success': False,
                'message': 'No devices found',
                'results': []
            }
        
        results = self.apply_template_to_devices(devices, config_commands, {}, save_config)
        
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        return {
            'success': True,
            'total_devices': len(devices),
            'successful': successful,
            'failed': failed,
            'results': results
        }
    
    def validate_template(self, template: str) -> Dict[str, Any]:
        """Validate a Jinja2 template syntax"""
        try:
            self.env.from_string(template)
            return {
                'valid': True,
                'error': None
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def get_template_variables(self, template: str) -> List[str]:
        """Extract variable names from a template"""
        try:
            template_obj = self.env.from_string(template)
            return list(template_obj.context.variables.keys())
        except Exception:
            return []
    
    def create_backup_before_change(
        self,
        device: Device,
        db: Session
    ) -> Optional[Dict[str, Any]]:
        """Create a backup before applying configuration changes"""
        from app.services.backup_engine import BackupEngine
        
        try:
            backup_engine = BackupEngine()
            result = backup_engine.perform_backup(device, db)
            
            if result['success']:
                logger.info(f"Pre-change backup created for device {device.name}")
            else:
                logger.warning(f"Pre-change backup failed for device {device.name}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating pre-change backup: {str(e)}")
            return None
    
    def rollback_config(
        self,
        device: Device,
        version: int,
        db: Session
    ) -> Dict[str, Any]:
        """Rollback a device configuration to a specific version"""
        try:
            from app.services.git_storage import GitStorageService
            from app.models.device import Configuration
            
            git_storage = GitStorageService()
            
            # Get the configuration from Git
            config = git_storage.get_configuration(device.id, device.name, version)
            
            if not config:
                return {
                    'success': False,
                    'error_message': f'Configuration version {version} not found'
                }
            
            # Parse config into commands
            commands = self._parse_config_commands(config)
            
            # Apply to device
            result = self.apply_config_to_device(device, commands, save_config=True)
            
            if result['success']:
                logger.info(f"Successfully rolled back device {device.name} to version {version}")
            else:
                logger.error(f"Rollback failed for device {device.name}: {result['error_message']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error rolling back device {device.name}: {str(e)}")
            return {
                'success': False,
                'error_message': str(e)
            }
    
    def get_predefined_templates(self) -> Dict[str, str]:
        """Get predefined templates for common tasks"""
        return {
            'cisco_snmp_config': """
! SNMP Configuration
snmp-server community {{ snmp_community }} ro
snmp-server location {{ location | default('Unknown') }}
snmp-server contact {{ contact | default('admin@example.com') }}
""",
            'cisco_ntp_config': """
! NTP Configuration
ntp server {{ ntp_server }}
ntp source {{ ntp_source_interface | default('Loopback0') }}
""",
            'cisco_acl_config': """
! Access List Configuration
ip access-list extended {{ acl_name }}
{% for rule in acl_rules %}
{{ rule }}
{% endfor %}
""",
            'mikrotik_snmp_config': """
/ snmp
set enabled=yes
set community="{{ snmp_community }}"
set location="{{ location | default('Unknown') }}"
set contact="{{ contact | default('admin@example.com') }}"
""",
            'mikrotik_ntp_config": """
/ system ntp client
set enabled=yes
set servers={{ ntp_server }}
set primary-ntp={{ ntp_server }}
""",
            'interface_description': """
! Interface Description Configuration
interface {{ interface_name }}
 description {{ description }}
{% if shutdown is defined and shutdown %}
 shutdown
{% else %}
 no shutdown
{% endif %}
"""
        }
    
    def get_template_by_name(self, template_name: str) -> Optional[str]:
        """Get a predefined template by name"""
        templates = self.get_predefined_templates()
        return templates.get(template_name)
