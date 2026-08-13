import os
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime
import git
from app.core.config import settings


class GitStorageService:
    """Service for managing Git-based configuration storage"""
    
    def __init__(self, repo_path: str = None):
        self.repo_path = repo_path or settings.GIT_REPO_PATH
        self._ensure_repo_exists()
    
    def _ensure_repo_exists(self):
        """Ensure the Git repository exists"""
        if not os.path.exists(self.repo_path):
            os.makedirs(self.repo_path, exist_ok=True)
        
        try:
            self.repo = git.Repo(self.repo_path)
        except git.InvalidGitRepositoryError:
            # Initialize new repository
            self.repo = git.Repo.init(self.repo_path)
            # Create initial commit
            readme_path = os.path.join(self.repo_path, "README.md")
            with open(readme_path, 'w') as f:
                f.write("# LANi-Platform Configuration Storage\n\n")
                f.write(f"Initialized on {datetime.now().isoformat()}\n")
            
            self.repo.index.add(["README.md"])
            self.repo.index.commit("Initial commit")
    
    def _get_device_path(self, device_id: int, device_name: str) -> str:
        """Get the directory path for a device's configurations"""
        # Sanitize device name for filesystem
        safe_name = "".join(c for c in device_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        device_dir = os.path.join(self.repo_path, f"device_{device_id}_{safe_name}")
        os.makedirs(device_dir, exist_ok=True)
        return device_dir
    
    def _calculate_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of configuration content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def store_configuration(
        self, 
        device_id: int, 
        device_name: str, 
        configuration: str, 
        version: int,
        commit_message: str = None
    ) -> Dict[str, Any]:
        """Store a configuration in Git repository"""
        try:
            device_dir = self._get_device_path(device_id, device_name)
            config_hash = self._calculate_hash(configuration)
            
            # Store configuration file
            filename = f"config_v{version}_{config_hash[:8]}.txt"
            file_path = os.path.join(device_dir, filename)
            
            with open(file_path, 'w') as f:
                f.write(configuration)
            
            # Add to Git
            self.repo.index.add([file_path])
            
            # Create commit
            if not commit_message:
                commit_message = f"Backup for device {device_name} (ID: {device_id}), version {version}"
            
            commit = self.repo.index.commit(commit_message)
            
            return {
                'success': True,
                'file_path': file_path,
                'config_hash': config_hash,
                'git_commit': commit.hexsha,
                'error_message': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'file_path': None,
                'config_hash': None,
                'git_commit': None,
                'error_message': str(e)
            }
    
    def get_configuration(self, device_id: int, device_name: str, version: int) -> Optional[str]:
        """Retrieve a specific configuration version"""
        try:
            device_dir = self._get_device_path(device_id, device_name)
            
            # Find the file for this version
            for filename in os.listdir(device_dir):
                if filename.startswith(f"config_v{version}_"):
                    file_path = os.path.join(device_dir, filename)
                    with open(file_path, 'r') as f:
                        return f.read()
            
            return None
            
        except Exception:
            return None
    
    def get_latest_configuration(self, device_id: int, device_name: str) -> Optional[Dict[str, Any]]:
        """Get the latest configuration for a device"""
        try:
            device_dir = self._get_device_path(device_id, device_name)
            
            # Find all config files and get the latest version
            config_files = [f for f in os.listdir(device_dir) if f.startswith("config_v")]
            
            if not config_files:
                return None
            
            # Sort by version number
            config_files.sort(key=lambda x: int(x.split('_v')[1].split('_')[0]))
            latest_file = config_files[-1]
            
            file_path = os.path.join(device_dir, latest_file)
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Extract version from filename
            version = int(latest_file.split('_v')[1].split('_')[0])
            config_hash = self._calculate_hash(content)
            
            return {
                'content': content,
                'version': version,
                'config_hash': config_hash,
                'file_path': file_path,
                'file_size': os.path.getsize(file_path)
            }
            
        except Exception:
            return None
    
    def get_configuration_history(self, device_id: int, device_name: str) -> list:
        """Get all configuration versions for a device"""
        try:
            device_dir = self._get_device_path(device_id, device_name)
            
            config_files = [f for f in os.listdir(device_dir) if f.startswith("config_v")]
            history = []
            
            for filename in config_files:
                file_path = os.path.join(device_dir, filename)
                
                # Extract version and hash from filename
                parts = filename.replace('.txt', '').split('_')
                version = int(parts[1])
                hash_part = parts[2]
                
                with open(file_path, 'r') as f:
                    content = f.read()
                
                history.append({
                    'version': version,
                    'config_hash': hash_part,
                    'file_path': file_path,
                    'file_size': os.path.getsize(file_path),
                    'created_at': datetime.fromtimestamp(os.path.getctime(file_path))
                })
            
            # Sort by version
            history.sort(key=lambda x: x['version'])
            return history
            
        except Exception:
            return []
    
    def compare_configurations(
        self, 
        device_id: int, 
        device_name: str, 
        version_a: int, 
        version_b: int
    ) -> Optional[str]:
        """Compare two configuration versions and return diff"""
        try:
            config_a = self.get_configuration(device_id, device_name, version_a)
            config_b = self.get_configuration(device_id, device_name, version_b)
            
            if not config_a or not config_b:
                return None
            
            # Use Git to generate diff
            device_dir = self._get_device_path(device_id, device_name)
            
            # Find file paths
            file_a = None
            file_b = None
            for filename in os.listdir(device_dir):
                if filename.startswith(f"config_v{version_a}_"):
                    file_a = os.path.join(device_dir, filename)
                if filename.startswith(f"config_v{version_b}_"):
                    file_b = os.path.join(device_dir, filename)
            
            if not file_a or not file_b:
                return None
            
            # Generate diff using Git
            diff = self.repo.git.diff(file_a, file_b)
            return diff
            
        except Exception:
            return None
    
    def delete_device_configurations(self, device_id: int, device_name: str) -> bool:
        """Delete all configurations for a device"""
        try:
            device_dir = self._get_device_path(device_id, device_name)
            
            # Remove all files in device directory
            for filename in os.listdir(device_dir):
                file_path = os.path.join(device_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            
            # Remove directory if empty
            if not os.listdir(device_dir):
                os.rmdir(device_dir)
            
            # Commit the deletion
            self.repo.index.add([device_dir])
            self.repo.index.commit(f"Deleted configurations for device {device_name} (ID: {device_id})")
            
            return True
            
        except Exception:
            return False
    
    def get_repository_info(self) -> Dict[str, Any]:
        """Get information about the Git repository"""
        try:
            return {
                'repo_path': self.repo_path,
                'branch': self.repo.active_branch.name,
                'commit_count': len(list(self.repo.iter_commits())),
                'last_commit': {
                    'hexsha': self.repo.head.commit.hexsha,
                    'message': self.repo.head.commit.message,
                    'author': str(self.repo.head.commit.author),
                    'date': datetime.fromtimestamp(self.repo.head.commit.committed_date).isoformat()
                }
            }
        except Exception:
            return {
                'repo_path': self.repo_path,
                'error': 'Could not retrieve repository info'
            }
