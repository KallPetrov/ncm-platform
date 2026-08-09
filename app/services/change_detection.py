import hashlib
import difflib
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.device import Device, Configuration
from app.services.git_storage import GitStorageService


class ChangeDetectionService:
    """Service for detecting and analyzing configuration changes"""
    
    def __init__(self):
        self.git_storage = GitStorageService()
    
    def calculate_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of configuration content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def detect_changes(
        self, 
        old_config: str, 
        new_config: str,
        device_name: str = "device"
    ) -> Dict[str, Any]:
        """Detect changes between two configurations"""
        old_hash = self.calculate_hash(old_config)
        new_hash = self.calculate_hash(new_config)
        
        has_changed = old_hash != new_hash
        
        if not has_changed:
            return {
                'has_changed': False,
                'old_hash': old_hash,
                'new_hash': new_hash,
                'change_summary': "No changes detected",
                'added_lines': 0,
                'removed_lines': 0,
                'changed_lines': 0
            }
        
        # Generate diff
        diff = self._generate_diff(old_config, new_config)
        
        # Analyze changes
        added_lines = len([line for line in diff if line.startswith('+')])
        removed_lines = len([line for line in diff if line.startswith('-')])
        changed_lines = added_lines + removed_lines
        
        # Generate change summary
        change_summary = self._generate_change_summary(
            old_config, new_config, device_name
        )
        
        return {
            'has_changed': True,
            'old_hash': old_hash,
            'new_hash': new_hash,
            'change_summary': change_summary,
            'added_lines': added_lines,
            'removed_lines': removed_lines,
            'changed_lines': changed_lines,
            'diff': diff
        }
    
    def _generate_diff(self, old_config: str, new_config: str) -> List[str]:
        """Generate unified diff between two configurations"""
        old_lines = old_config.splitlines(keepends=True)
        new_lines = new_config.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile='old_config',
            tofile='new_config',
            lineterm=''
        )
        
        return list(diff)
    
    def _generate_change_summary(
        self, 
        old_config: str, 
        new_config: str,
        device_name: str
    ) -> str:
        """Generate a human-readable summary of changes"""
        old_lines = set(old_config.splitlines())
        new_lines = set(new_config.splitlines())
        
        added = new_lines - old_lines
        removed = old_lines - new_lines
        
        summary_parts = []
        
        if added:
            # Try to identify what was added
            added_sample = list(added)[:3]
            summary_parts.append(f"Added {len(added)} lines")
        
        if removed:
            # Try to identify what was removed
            removed_sample = list(removed)[:3]
            summary_parts.append(f"Removed {len(removed)} lines")
        
        if not summary_parts:
            return "Configuration changed (whitespace or formatting)"
        
        return "; ".join(summary_parts)
    
    def analyze_configuration_changes(
        self,
        device_id: int,
        device_name: str,
        db: Session
    ) -> Dict[str, Any]:
        """Analyze recent configuration changes for a device"""
        # Get latest two configurations
        configs = db.query(Configuration).filter(
            Configuration.device_id == device_id
        ).order_by(Configuration.version.desc()).limit(2).all()
        
        if len(configs) < 2:
            return {
                'has_changes': False,
                'message': 'Not enough configuration versions to compare'
            }
        
        latest_config = configs[0]
        previous_config = configs[1]
        
        # Get actual content from Git storage
        latest_content = self.git_storage.get_configuration(
            device_id, device_name, latest_config.version
        )
        previous_content = self.git_storage.get_configuration(
            device_id, device_name, previous_config.version
        )
        
        if not latest_content or not previous_content:
            return {
                'has_changes': False,
                'message': 'Could not retrieve configuration content'
            }
        
        # Detect changes
        changes = self.detect_changes(
            previous_content, latest_content, device_name
        )
        
        return {
            'device_id': device_id,
            'device_name': device_name,
            'previous_version': previous_config.version,
            'latest_version': latest_config.version,
            'previous_hash': previous_config.config_hash,
            'latest_hash': latest_config.config_hash,
            **changes
        }
    
    def get_changed_lines(
        self, 
        old_config: str, 
        new_config: str,
        context_lines: int = 3
    ) -> Dict[str, Any]:
        """Get detailed changed lines with context"""
        old_lines = old_config.splitlines()
        new_lines = new_config.splitlines()
        
        differ = difflib.Differ()
        diff = list(differ.compare(old_lines, new_lines))
        
        changes = []
        current_change = []
        line_number_old = 0
        line_number_new = 0
        
        for line in diff:
            if line.startswith('  '):
                # Unchanged line
                line_number_old += 1
                line_number_new += 1
                if current_change:
                    changes.append({
                        'old_line_start': current_change[0].get('old_line'),
                        'new_line_start': current_change[0].get('new_line'),
                        'lines': current_change
                    })
                    current_change = []
            elif line.startswith('- '):
                # Removed line
                line_number_old += 1
                current_change.append({
                    'type': 'removed',
                    'content': line[2:],
                    'old_line': line_number_old,
                    'new_line': None
                })
            elif line.startswith('+ '):
                # Added line
                line_number_new += 1
                current_change.append({
                    'type': 'added',
                    'content': line[2:],
                    'old_line': None,
                    'new_line': line_number_new
                })
            elif line.startswith('? '):
                # Line change indicator (skip for now)
                pass
        
        # Add any remaining changes
        if current_change:
            changes.append({
                'old_line_start': current_change[0].get('old_line'),
                'new_line_start': current_change[0].get('new_line'),
                'lines': current_change
            })
        
        return {
            'total_changes': len(changes),
            'changes': changes
        }
    
    def detect_security_changes(
        self, 
        old_config: str, 
        new_config: str
    ) -> Dict[str, Any]:
        """Detect security-related configuration changes"""
        security_keywords = [
            'password', 'secret', 'key', 'crypto', 'ssh',
            'acl', 'firewall', 'security', 'authentication',
            'authorization', 'encryption', 'certificate'
        ]
        
        old_lines = old_config.lower().splitlines()
        new_lines = new_config.lower().splitlines()
        
        security_changes = []
        
        for i, (old_line, new_line) in enumerate(zip(old_lines, new_lines)):
            if old_line != new_line:
                # Check if any security keyword is in the changed line
                for keyword in security_keywords:
                    if keyword in old_line or keyword in new_line:
                        security_changes.append({
                            'line_number': i + 1,
                            'keyword': keyword,
                            'old_line': old_line.strip(),
                            'new_line': new_line.strip()
                        })
                        break
        
        return {
            'has_security_changes': len(security_changes) > 0,
            'security_changes': security_changes,
            'total_security_changes': len(security_changes)
        }
    
    def compare_configurations_by_hash(
        self,
        hash_a: str,
        hash_b: str,
        db: Session
    ) -> Optional[Dict[str, Any]]:
        """Compare two configurations by their hashes"""
        config_a = db.query(Configuration).filter(
            Configuration.config_hash == hash_a
        ).first()
        
        config_b = db.query(Configuration).filter(
            Configuration.config_hash == hash_b
        ).first()
        
        if not config_a or not config_b:
            return None
        
        # Get device info
        device = db.query(Device).filter(Device.id == config_a.device_id).first()
        if not device:
            return None
        
        # Get content from Git
        content_a = self.git_storage.get_configuration(
            device.id, device.name, config_a.version
        )
        content_b = self.git_storage.get_configuration(
            device.id, device.name, config_b.version
        )
        
        if not content_a or not content_b:
            return None
        
        return self.detect_changes(content_a, content_b, device.name)
