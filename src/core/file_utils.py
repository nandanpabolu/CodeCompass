"""
File utilities for code analysis.
"""

import os
import stat
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import chardet
from loguru import logger


class FileUtils:
    """File utilities for code analysis."""
    
    def __init__(self, settings):
        self.settings = settings
        self.max_file_size = settings.server.max_file_size_mb * 1024 * 1024
        
        logger.info("FileUtils initialized")
    
    async def read_file(
        self,
        path: str,
        offset: int = 0,
        length: int = 2000
    ) -> Tuple[str, int]:
        """Read file contents with pagination."""
        try:
            file_path = Path(path)
            
            # Check if file exists
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {path}")
            
            # Check if it's a file
            if not file_path.is_file():
                raise ValueError(f"Path is not a file: {path}")
            
            # Check file size
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                raise ValueError(f"File too large: {file_size} bytes (max: {self.max_file_size})")
            
            # Read file with encoding detection
            with open(file_path, 'rb') as f:
                raw_data = f.read()
            
            # Detect encoding
            encoding = self._detect_encoding(raw_data)
            
            # Decode content
            try:
                content = raw_data.decode(encoding)
            except UnicodeDecodeError:
                # Fallback to utf-8 with error handling
                content = raw_data.decode('utf-8', errors='replace')
            
            # Apply pagination
            total_bytes = len(content.encode(encoding))
            
            if offset > 0 or length < len(content):
                # Convert byte offset to character offset
                char_offset = len(content[:offset].encode(encoding))
                char_length = len(content[char_offset:char_offset + length].encode(encoding))
                
                content = content[char_offset:char_offset + char_length]
            
            logger.info(f"File read: {path} ({len(content)} chars, {total_bytes} bytes)")
            return content, total_bytes
            
        except Exception as e:
            logger.error(f"Read file error: {e}")
            raise
    
    def _detect_encoding(self, data: bytes) -> str:
        """Detect file encoding."""
        try:
            result = chardet.detect(data)
            encoding = result.get('encoding', 'utf-8')
            confidence = result.get('confidence', 0)
            
            # Use detected encoding if confidence is high enough
            if confidence > 0.7:
                return encoding
            else:
                return 'utf-8'
                
        except Exception:
            return 'utf-8'
    
    async def get_file_info(self, path: str) -> Dict[str, Any]:
        """Get file metadata and information."""
        try:
            file_path = Path(path)
            
            # Check if file exists
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {path}")
            
            # Get file stats
            stat_info = file_path.stat()
            
            # Detect language from extension
            language = self._detect_language_from_extension(file_path.suffix)
            
            # Get file size
            file_size = stat_info.st_size
            
            # Check if file is readable
            is_readable = os.access(file_path, os.R_OK)
            
            # Get file permissions
            permissions = stat.filemode(stat_info.st_mode)
            
            info = {
                "path": str(file_path),
                "name": file_path.name,
                "size": file_size,
                "size_mb": round(file_size / (1024 * 1024), 2),
                "language": language,
                "extension": file_path.suffix,
                "is_readable": is_readable,
                "permissions": permissions,
                "modified": stat_info.st_mtime,
                "created": stat_info.st_ctime,
                "is_file": file_path.is_file(),
                "is_directory": file_path.is_dir(),
                "parent": str(file_path.parent)
            }
            
            logger.info(f"File info retrieved: {path}")
            return info
            
        except Exception as e:
            logger.error(f"Get file info error: {e}")
            raise
    
    def _detect_language_from_extension(self, extension: str) -> str:
        """Detect programming language from file extension."""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.r': 'r',
            '.m': 'matlab',
            '.sh': 'bash',
            '.bash': 'bash',
            '.zsh': 'zsh',
            '.fish': 'fish',
            '.ps1': 'powershell',
            '.bat': 'batch',
            '.cmd': 'batch',
            '.sql': 'sql',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.less': 'less',
            '.xml': 'xml',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
            '.ini': 'ini',
            '.cfg': 'ini',
            '.conf': 'ini',
            '.md': 'markdown',
            '.rst': 'restructuredtext',
            '.txt': 'text',
            '.log': 'log'
        }
        
        return language_map.get(extension.lower(), 'unknown')
    
    async def list_files(
        self,
        directory: str,
        recursive: bool = True,
        include_hidden: bool = False
    ) -> List[Dict[str, Any]]:
        """List files in a directory."""
        try:
            dir_path = Path(directory)
            
            if not dir_path.exists():
                raise FileNotFoundError(f"Directory not found: {directory}")
            
            if not dir_path.is_dir():
                raise ValueError(f"Path is not a directory: {directory}")
            
            files = []
            
            if recursive:
                pattern = "**/*"
            else:
                pattern = "*"
            
            for file_path in dir_path.glob(pattern):
                # Skip hidden files if not requested
                if not include_hidden and file_path.name.startswith('.'):
                    continue
                
                # Skip if it's a directory
                if file_path.is_dir():
                    continue
                
                # Check if file should be included
                if self._should_include_file(file_path):
                    try:
                        file_info = await self.get_file_info(str(file_path))
                        files.append(file_info)
                    except Exception as e:
                        logger.warning(f"Error getting info for {file_path}: {e}")
                        continue
            
            logger.info(f"Listed {len(files)} files in {directory}")
            return files
            
        except Exception as e:
            logger.error(f"List files error: {e}")
            raise
    
    def _should_include_file(self, file_path: Path) -> bool:
        """Check if file should be included in listings."""
        # Check ignore patterns
        for pattern in self.settings.repositories.ignore_patterns:
            if file_path.match(pattern):
                return False
        
        # Check file size
        try:
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                return False
        except OSError:
            return False
        
        return True
