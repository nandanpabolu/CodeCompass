"""
Safety utilities for path validation and sandboxing.
"""

import os
from pathlib import Path
from typing import List, Set
from loguru import logger


class PathValidator:
    """Path validation and sandboxing utilities."""
    
    def __init__(self, allowed_roots: List[str]):
        self.allowed_roots = [Path(root).resolve() for root in allowed_roots]
        self._validate_roots()
        
        logger.info(f"PathValidator initialized with roots: {self.allowed_roots}")
    
    def _validate_roots(self) -> None:
        """Validate that all allowed roots exist and are accessible."""
        valid_roots = []
        
        for root in self.allowed_roots:
            try:
                if root.exists() and root.is_dir():
                    # Check if we can read from the directory
                    os.access(root, os.R_OK)
                    valid_roots.append(root)
                else:
                    logger.warning(f"Invalid root path: {root}")
            except Exception as e:
                logger.warning(f"Error validating root {root}: {e}")
        
        self.allowed_roots = valid_roots
        
        if not self.allowed_roots:
            # Fallback to current directory
            self.allowed_roots = [Path.cwd()]
            logger.warning("No valid roots found, using current directory")
    
    def is_safe_path(self, path: str) -> bool:
        """Check if a path is safe to access."""
        try:
            path_obj = Path(path).resolve()
            
            # Check for path traversal attempts
            if self._has_path_traversal(path):
                logger.warning(f"Path traversal detected: {path}")
                return False
            
            # Check if path is within allowed roots
            if not self._is_within_allowed_roots(path_obj):
                logger.warning(f"Path outside allowed roots: {path}")
                return False
            
            # Check if path exists
            if not path_obj.exists():
                logger.warning(f"Path does not exist: {path}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating path {path}: {e}")
            return False
    
    def _has_path_traversal(self, path: str) -> bool:
        """Check for path traversal patterns."""
        # Check for common path traversal patterns
        dangerous_patterns = [
            "..",
            "../",
            "..\\",
            "..%2f",
            "..%5c",
            "..%252f",
            "..%255c"
        ]
        
        path_lower = path.lower()
        for pattern in dangerous_patterns:
            if pattern in path_lower:
                return True
        
        # Check for absolute paths that might escape
        if os.path.isabs(path):
            # Allow absolute paths only if they're within allowed roots
            path_obj = Path(path).resolve()
            if not self._is_within_allowed_roots(path_obj):
                return True
        
        return False
    
    def _is_within_allowed_roots(self, path: Path) -> bool:
        """Check if path is within any of the allowed roots."""
        try:
            for root in self.allowed_roots:
                try:
                    # Check if path is within this root
                    path.relative_to(root)
                    return True
                except ValueError:
                    # Path is not relative to this root, try next
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking path within roots: {e}")
            return False
    
    def sanitize_path(self, path: str) -> str:
        """Sanitize a path by removing dangerous elements."""
        try:
            # Remove path traversal elements
            path_parts = Path(path).parts
            
            # Filter out dangerous parts
            safe_parts = []
            for part in path_parts:
                if part not in [".", ".."] and not part.startswith("."):
                    safe_parts.append(part)
            
            # Reconstruct path
            sanitized = Path(*safe_parts)
            
            # Ensure it's still within allowed roots
            if self.is_safe_path(str(sanitized)):
                return str(sanitized)
            else:
                # Return the first allowed root as fallback
                return str(self.allowed_roots[0])
                
        except Exception as e:
            logger.error(f"Error sanitizing path {path}: {e}")
            return str(self.allowed_roots[0])
    
    def get_safe_path(self, path: str) -> str:
        """Get a safe version of the path."""
        if self.is_safe_path(path):
            return path
        else:
            return self.sanitize_path(path)
    
    def list_safe_files(self, directory: str, recursive: bool = True) -> List[str]:
        """List files in a directory, ensuring all paths are safe."""
        try:
            if not self.is_safe_path(directory):
                logger.warning(f"Unsafe directory: {directory}")
                return []
            
            dir_path = Path(directory)
            safe_files = []
            
            if recursive:
                pattern = "**/*"
            else:
                pattern = "*"
            
            for file_path in dir_path.glob(pattern):
                if file_path.is_file() and self.is_safe_path(str(file_path)):
                    safe_files.append(str(file_path))
            
            return safe_files
            
        except Exception as e:
            logger.error(f"Error listing safe files in {directory}: {e}")
            return []
    
    def get_allowed_roots(self) -> List[str]:
        """Get list of allowed root paths."""
        return [str(root) for root in self.allowed_roots]
    
    def add_allowed_root(self, root: str) -> bool:
        """Add a new allowed root path."""
        try:
            root_path = Path(root).resolve()
            
            if root_path.exists() and root_path.is_dir():
                if root_path not in self.allowed_roots:
                    self.allowed_roots.append(root_path)
                    logger.info(f"Added allowed root: {root_path}")
                    return True
                else:
                    logger.info(f"Root already allowed: {root_path}")
                    return True
            else:
                logger.warning(f"Invalid root path: {root}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding allowed root {root}: {e}")
            return False
    
    def remove_allowed_root(self, root: str) -> bool:
        """Remove an allowed root path."""
        try:
            root_path = Path(root).resolve()
            
            if root_path in self.allowed_roots:
                self.allowed_roots.remove(root_path)
                logger.info(f"Removed allowed root: {root_path}")
                return True
            else:
                logger.warning(f"Root not found: {root}")
                return False
                
        except Exception as e:
            logger.error(f"Error removing allowed root {root}: {e}")
            return False
