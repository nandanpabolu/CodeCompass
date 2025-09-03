"""
Core code analysis engine.
"""

import asyncio
import re
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import chardet
from loguru import logger

from .search import SearchEngine
from .explainer import CodeExplainer
from .file_utils import FileUtils


class CodeAnalyzer:
    """Main code analysis engine."""
    
    def __init__(self, settings):
        self.settings = settings
        self.search_engine = SearchEngine(settings)
        self.explainer = CodeExplainer(settings)
        self.file_utils = FileUtils(settings)
        
        logger.info("CodeAnalyzer initialized")
    
    async def search_code(
        self,
        query: str,
        regex: bool = False,
        case_sensitive: bool = False,
        path_prefix: str = "",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search for code using text or regex patterns."""
        try:
            results = await self.search_engine.search(
                query=query,
                regex=regex,
                case_sensitive=case_sensitive,
                path_prefix=path_prefix,
                limit=limit
            )
            
            logger.info(f"Search completed: {len(results)} results for query '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise
    
    async def read_file(
        self,
        path: str,
        offset: int = 0,
        length: int = 2000
    ) -> Tuple[str, int]:
        """Read file contents with pagination."""
        try:
            content, total_bytes = await self.file_utils.read_file(
                path=path,
                offset=offset,
                length=length
            )
            
            logger.info(f"File read: {path} ({len(content)} bytes)")
            return content, total_bytes
            
        except Exception as e:
            logger.error(f"Read file error: {e}")
            raise
    
    async def explain_range(
        self,
        path: str,
        start_line: int,
        end_line: int,
        code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Explain a range of code."""
        try:
            if code is None:
                # Read the code from file
                content, _ = await self.read_file(path)
                lines = content.split('\n')
                code = '\n'.join(lines[start_line-1:end_line])
            
            explanation = await self.explainer.explain(
                code=code,
                path=path,
                start_line=start_line,
                end_line=end_line
            )
            
            logger.info(f"Code explanation completed: {path}:{start_line}-{end_line}")
            return explanation
            
        except Exception as e:
            logger.error(f"Explain range error: {e}")
            raise
    
    async def list_todos(self, path_prefix: str = "") -> List[Dict[str, Any]]:
        """List TODO/FIXME comments in the codebase."""
        try:
            todos = await self.search_engine.find_todos(path_prefix=path_prefix)
            
            logger.info(f"TODO search completed: {len(todos)} items found")
            return todos
            
        except Exception as e:
            logger.error(f"List todos error: {e}")
            raise
    
    async def get_file_info(self, path: str) -> Dict[str, Any]:
        """Get file metadata and information."""
        try:
            info = await self.file_utils.get_file_info(path)
            
            logger.info(f"File info retrieved: {path}")
            return info
            
        except Exception as e:
            logger.error(f"Get file info error: {e}")
            raise
