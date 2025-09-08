#!/usr/bin/env python3
"""
CodeCompass MCP Server

Main entry point for the MCP server that provides codebase analysis tools.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from pydantic import BaseModel, Field

# Add the src directory to the path for imports
sys.path.append(str(Path(__file__).parent))

from core.analyzer import CodeAnalyzer
from config.settings import Settings
from utils.safety import PathValidator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("codecompass")

# Global instances
analyzer: Optional[CodeAnalyzer] = None
settings: Optional[Settings] = None
path_validator: Optional[PathValidator] = None


class SearchCodeRequest(BaseModel):
    """Request model for code search."""
    query: str = Field(..., description="Search query")
    regex: bool = Field(False, description="Use regex search")
    case_sensitive: bool = Field(False, description="Case sensitive search")
    path_prefix: str = Field("", description="Limit search to path prefix")
    limit: int = Field(50, description="Maximum number of results")


class ReadFileRequest(BaseModel):
    """Request model for file reading."""
    path: str = Field(..., description="File path to read")
    offset: int = Field(0, description="Byte offset to start reading")
    length: int = Field(2000, description="Number of bytes to read")


class ExplainRangeRequest(BaseModel):
    """Request model for code explanation."""
    path: str = Field(..., description="File path")
    start_line: int = Field(..., description="Start line number")
    end_line: int = Field(..., description="End line number")


class ListTodosRequest(BaseModel):
    """Request model for TODO listing."""
    path_prefix: str = Field("", description="Limit search to path prefix")


class GetFileInfoRequest(BaseModel):
    """Request model for file info."""
    path: str = Field(..., description="File path")


async def initialize_server():
    """Initialize the server components."""
    global analyzer, settings, path_validator
    
    try:
        # Load settings
        settings = Settings()
        
        # Initialize path validator
        path_validator = PathValidator(settings.repositories.roots)
        
        # Initialize analyzer
        analyzer = CodeAnalyzer(settings)
        
        logger.info("CodeCompass MCP Server initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize server: {e}")
        raise


@server.tool("search_code")
async def search_code(request: SearchCodeRequest) -> Dict[str, Any]:
    """Search for code using text or regex patterns."""
    try:
        if not analyzer:
            raise RuntimeError("Server not initialized")
        
        # Validate path
        if request.path_prefix and not path_validator.is_safe_path(request.path_prefix):
            raise ValueError("Invalid path prefix")
        
        # Perform search
        results = await analyzer.search_code(
            query=request.query,
            regex=request.regex,
            case_sensitive=request.case_sensitive,
            path_prefix=request.path_prefix,
            limit=request.limit
        )
        
        return {
            "items": results,
            "total": len(results),
            "query": request.query
        }
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return {"error": str(e), "items": []}


@server.tool("read_file")
async def read_file(request: ReadFileRequest) -> Dict[str, Any]:
    """Read file contents with pagination."""
    try:
        if not analyzer:
            raise RuntimeError("Server not initialized")
        
        # Validate path
        if not path_validator.is_safe_path(request.path):
            raise ValueError("Invalid file path")
        
        # Read file
        content, total_bytes = await analyzer.read_file(
            path=request.path,
            offset=request.offset,
            length=request.length
        )
        
        return {
            "content": content,
            "total_bytes": total_bytes,
            "offset": request.offset,
            "length": len(content)
        }
        
    except Exception as e:
        logger.error(f"Read file error: {e}")
        return {"error": str(e), "content": ""}


@server.tool("explain_range")
async def explain_range(request: ExplainRangeRequest) -> Dict[str, Any]:
    """Explain a range of code."""
    try:
        if not analyzer:
            raise RuntimeError("Server not initialized")
        
        # Validate path
        if not path_validator.is_safe_path(request.path):
            raise ValueError("Invalid file path")
        
        # Explain code
        explanation = await analyzer.explain_range(
            path=request.path,
            start_line=request.start_line,
            end_line=request.end_line
        )
        
        return explanation
        
    except Exception as e:
        logger.error(f"Explain range error: {e}")
        return {"error": str(e), "summary": ""}


@server.tool("list_todos")
async def list_todos(request: ListTodosRequest) -> Dict[str, Any]:
    """List TODO/FIXME comments in the codebase."""
    try:
        if not analyzer:
            raise RuntimeError("Server not initialized")
        
        # Validate path
        if request.path_prefix and not path_validator.is_safe_path(request.path_prefix):
            raise ValueError("Invalid path prefix")
        
        # Find TODOs
        todos = await analyzer.list_todos(path_prefix=request.path_prefix)
        
        return {
            "items": todos,
            "total": len(todos)
        }
        
    except Exception as e:
        logger.error(f"List todos error: {e}")
        return {"error": str(e), "items": []}


@server.tool("get_file_info")
async def get_file_info(request: GetFileInfoRequest) -> Dict[str, Any]:
    """Get file metadata and information."""
    try:
        if not analyzer:
            raise RuntimeError("Server not initialized")
        
        # Validate path
        if not path_validator.is_safe_path(request.path):
            raise ValueError("Invalid file path")
        
        # Get file info
        info = await analyzer.get_file_info(request.path)
        
        return info
        
    except Exception as e:
        logger.error(f"Get file info error: {e}")
        return {"error": str(e)}


async def main():
    """Main entry point for the MCP server."""
    try:
        # Initialize server
        await initialize_server()
        
        # Run server
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
            
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
