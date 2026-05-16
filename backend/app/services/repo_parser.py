"""Repository parser service for cloning and analyzing repositories"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List, Tuple
from urllib.parse import urlparse
import git
from git import Repo


class RepoParser:
    """Parse and prepare repositories for analysis"""
    
    SUPPORTED_EXTENSIONS = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
    }
    
    IGNORE_DIRS = {
        'node_modules', 'venv', 'env', '.venv', '__pycache__',
        '.git', '.idea', '.vscode', 'dist', 'build', 'target',
        '.pytest_cache', '.mypy_cache', 'coverage', '.next'
    }
    
    IGNORE_FILES = {
        '.pyc', '.pyo', '.pyd', '.so', '.dll', '.dylib',
        '.class', '.o', '.obj', '.exe', '.log'
    }
    
    def __init__(self):
        self.temp_dir: Optional[str] = None
    
    def is_github_url(self, path: str) -> bool:
        """Check if the path is a GitHub URL"""
        try:
            parsed = urlparse(path)
            return parsed.netloc in ['github.com', 'www.github.com']
        except Exception:
            return False
    
    def clone_repository(self, repo_url: str) -> str:
        """Clone a GitHub repository to a temporary directory"""
        self.temp_dir = tempfile.mkdtemp(prefix='codelens_')
        
        try:
            print(f"Cloning repository: {repo_url}")
            Repo.clone_from(repo_url, self.temp_dir, depth=1)
            print(f"Repository cloned to: {self.temp_dir}")
            return self.temp_dir
        except git.GitCommandError as e:
            self.cleanup()
            raise ValueError(f"Failed to clone repository: {str(e)}")
    
    def get_repo_path(self, path: str) -> str:
        """Get the repository path (clone if URL, validate if local)"""
        if self.is_github_url(path):
            return self.clone_repository(path)
        else:
            # Validate local path
            local_path = Path(path).resolve()
            if not local_path.exists():
                raise ValueError(f"Path does not exist: {path}")
            if not local_path.is_dir():
                raise ValueError(f"Path is not a directory: {path}")
            return str(local_path)
    
    def should_ignore_dir(self, dir_name: str) -> bool:
        """Check if directory should be ignored"""
        return dir_name in self.IGNORE_DIRS or dir_name.startswith('.')
    
    def should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored"""
        # Check file extension
        if file_path.suffix in self.IGNORE_FILES:
            return True
        
        # Check if it's a supported file type
        if file_path.suffix not in self.SUPPORTED_EXTENSIONS:
            return True
        
        # Check file size (ignore files > 1MB)
        try:
            if file_path.stat().st_size > 1024 * 1024:
                return True
        except OSError:
            return True
        
        return False
    
    def scan_repository(self, repo_path: str) -> Tuple[List[Path], dict]:
        """
        Scan repository and return list of files to analyze
        
        Returns:
            Tuple of (file_paths, stats) where stats contains:
            - total_files: total number of files found
            - total_lines: total lines of code
            - languages: dict of language counts
        """
        repo_path = Path(repo_path)
        files_to_analyze: List[Path] = []
        stats = {
            'total_files': 0,
            'total_lines': 0,
            'languages': {}
        }
        
        for root, dirs, files in os.walk(repo_path):
            # Remove ignored directories from traversal
            dirs[:] = [d for d in dirs if not self.should_ignore_dir(d)]
            
            for file in files:
                file_path = Path(root) / file
                
                if self.should_ignore_file(file_path):
                    continue
                
                # Get language
                language = self.SUPPORTED_EXTENSIONS.get(file_path.suffix)
                if language:
                    files_to_analyze.append(file_path)
                    stats['total_files'] += 1
                    stats['languages'][language] = stats['languages'].get(language, 0) + 1
                    
                    # Count lines
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = len(f.readlines())
                            stats['total_lines'] += lines
                    except Exception:
                        pass
        
        return files_to_analyze, stats
    
    def get_primary_language(self, stats: dict) -> Optional[str]:
        """Determine the primary language of the repository"""
        if not stats.get('languages'):
            return None
        
        # Return language with most files
        return max(stats['languages'].items(), key=lambda x: x[1])[0]
    
    def cleanup(self):
        """Clean up temporary directory if it was created"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                print(f"Cleaned up temporary directory: {self.temp_dir}")
            except Exception as e:
                print(f"Warning: Failed to clean up {self.temp_dir}: {e}")
            finally:
                self.temp_dir = None
    
    def __del__(self):
        """Ensure cleanup on deletion"""
        self.cleanup()

# Made with Bob
