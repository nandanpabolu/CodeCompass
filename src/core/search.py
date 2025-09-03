"""
Search engine for code analysis.
"""

import asyncio
import re
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import glob
from loguru import logger

from .file_utils import FileUtils


class SearchEngine:
    """Search engine for code analysis."""
    
    def __init__(self, settings):
        self.settings = settings
        self.file_utils = FileUtils(settings)
        
        # TODO patterns
        self.todo_patterns = [
            r'TODO[:\s]*(.+)',
            r'FIXME[:\s]*(.+)',
            r'HACK[:\s]*(.+)',
            r'NOTE[:\s]*(.+)',
            r'XXX[:\s]*(.+)',
            r'BUG[:\s]*(.+)'
        ]
        
        logger.info("SearchEngine initialized")
    
    async def search(
        self,
        query: str,
        regex: bool = False,
        case_sensitive: bool = False,
        path_prefix: str = "",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search for code using text or regex patterns."""
        try:
            results = []
            search_paths = self._get_search_paths(path_prefix)
            
            for file_path in search_paths:
                if len(results) >= limit:
                    break
                
                try:
                    # Read file content
                    content, _ = await self.file_utils.read_file(file_path)
                    
                    # Search in file
                    file_results = self._search_in_file(
                        content=content,
                        file_path=file_path,
                        query=query,
                        regex=regex,
                        case_sensitive=case_sensitive
                    )
                    
                    results.extend(file_results)
                    
                except Exception as e:
                    logger.warning(f"Error searching in {file_path}: {e}")
                    continue
            
            # Sort by relevance and limit results
            results = results[:limit]
            
            logger.info(f"Search completed: {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise
    
    def _get_search_paths(self, path_prefix: str = "") -> List[str]:
        """Get list of files to search."""
        search_paths = []
        
        # Get repository roots
        roots = self.settings.repositories.roots or ["."]
        
        for root in roots:
            root_path = Path(root)
            if not root_path.exists():
                continue
            
            # Build search pattern
            if path_prefix:
                search_pattern = str(root_path / path_prefix / "**" / "*")
            else:
                search_pattern = str(root_path / "**" / "*")
            
            # Get files matching pattern
            for file_path in glob.glob(search_pattern, recursive=True):
                if os.path.isfile(file_path) and self._should_search_file(file_path):
                    search_paths.append(file_path)
        
        return search_paths
    
    def _should_search_file(self, file_path: str) -> bool:
        """Check if file should be searched."""
        file_path = Path(file_path)
        
        # Check file extension
        if file_path.suffix not in ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.go', '.rs', '.php', '.rb', '.swift', '.kt']:
            return False
        
        # Check ignore patterns
        for pattern in self.settings.repositories.ignore_patterns:
            if file_path.match(pattern):
                return False
        
        # Check file size
        try:
            file_size = file_path.stat().st_size
            max_size = self.settings.server.max_file_size_mb * 1024 * 1024
            if file_size > max_size:
                return False
        except OSError:
            return False
        
        return True
    
    def _search_in_file(
        self,
        content: str,
        file_path: str,
        query: str,
        regex: bool = False,
        case_sensitive: bool = False
    ) -> List[Dict[str, Any]]:
        """Search for query in file content."""
        results = []
        lines = content.split('\n')
        
        try:
            if regex:
                # Regex search
                flags = 0 if case_sensitive else re.IGNORECASE
                pattern = re.compile(query, flags)
                
                for line_num, line in enumerate(lines, 1):
                    if pattern.search(line):
                        results.append({
                            'path': file_path,
                            'line': line_num,
                            'snippet': line.strip(),
                            'match': pattern.search(line).group()
                        })
            else:
                # Text search
                search_text = query if case_sensitive else query.lower()
                
                for line_num, line in enumerate(lines, 1):
                    line_text = line if case_sensitive else line.lower()
                    
                    if search_text in line_text:
                        # Find the position of the match
                        start_pos = line_text.find(search_text)
                        end_pos = start_pos + len(search_text)
                        
                        # Create snippet with context
                        snippet = line.strip()
                        
                        results.append({
                            'path': file_path,
                            'line': line_num,
                            'snippet': snippet,
                            'match': query
                        })
        
        except re.error as e:
            logger.warning(f"Regex error in {file_path}: {e}")
        
        return results
    
    async def find_todos(self, path_prefix: str = "") -> List[Dict[str, Any]]:
        """Find TODO/FIXME comments in the codebase."""
        try:
            todos = []
            search_paths = self._get_search_paths(path_prefix)
            
            for file_path in search_paths:
                try:
                    # Read file content
                    content, _ = await self.file_utils.read_file(file_path)
                    
                    # Find TODOs in file
                    file_todos = self._find_todos_in_file(content, file_path)
                    todos.extend(file_todos)
                    
                except Exception as e:
                    logger.warning(f"Error searching TODOs in {file_path}: {e}")
                    continue
            
            logger.info(f"TODO search completed: {len(todos)} items found")
            return todos
            
        except Exception as e:
            logger.error(f"TODO search error: {e}")
            raise
    
    def _find_todos_in_file(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Find TODO comments in file content."""
        todos = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern in self.todo_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    todo_text = match.group(1).strip()
                    todo_type = match.group(0).split(':')[0].strip()
                    
                    todos.append({
                        'path': file_path,
                        'line': line_num,
                        'text': todo_text,
                        'type': todo_type,
                        'snippet': line.strip()
                    })
        
        return todos
