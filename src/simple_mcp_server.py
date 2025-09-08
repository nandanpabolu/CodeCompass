#!/usr/bin/env python3
"""
Simple MCP Server for testing

A basic MCP server to test the setup and functionality.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Initialize MCP server
server = Server("codecompass")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="search_code",
            description="Search for code using text or regex patterns",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "regex": {
                        "type": "boolean",
                        "description": "Use regex search",
                        "default": False
                    },
                    "path_prefix": {
                        "type": "string",
                        "description": "Limit search to path prefix",
                        "default": ""
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 50
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="read_file",
            description="Read file contents with pagination",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "File path to read"
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Byte offset to start reading",
                        "default": 0
                    },
                    "length": {
                        "type": "integer",
                        "description": "Number of bytes to read",
                        "default": 2000
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="list_todos",
            description="List TODO/FIXME comments in the codebase",
            inputSchema={
                "type": "object",
                "properties": {
                    "path_prefix": {
                        "type": "string",
                        "description": "Limit search to path prefix",
                        "default": ""
                    }
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    try:
        if name == "search_code":
            query = arguments.get("query", "")
            regex = arguments.get("regex", False)
            path_prefix = arguments.get("path_prefix", "")
            limit = arguments.get("limit", 50)
            
            # Simple search implementation
            results = []
            try:
                import os
                import glob
                
                # Search in current directory
                search_path = path_prefix if path_prefix else "."
                pattern = f"{search_path}/**/*.py"
                
                for file_path in glob.glob(pattern, recursive=True):
                    if len(results) >= limit:
                        break
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            lines = content.split('\n')
                            
                            for line_num, line in enumerate(lines, 1):
                                if query.lower() in line.lower():
                                    results.append({
                                        "path": file_path,
                                        "line": line_num,
                                        "snippet": line.strip()
                                    })
                                    if len(results) >= limit:
                                        break
                    except Exception:
                        continue
                        
            except Exception as e:
                return [TextContent(type="text", text=f"Search error: {e}")]
            
            return [TextContent(type="text", text=json.dumps({
                "items": results,
                "total": len(results),
                "query": query
            }, indent=2))]
        
        elif name == "read_file":
            path = arguments.get("path", "")
            offset = arguments.get("offset", 0)
            length = arguments.get("length", 2000)
            
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    total_bytes = len(content.encode('utf-8'))
                    
                    # Apply pagination
                    if offset > 0 or length < len(content):
                        content = content[offset:offset + length]
                    
                    return [TextContent(type="text", text=json.dumps({
                        "content": content,
                        "total_bytes": total_bytes,
                        "offset": offset,
                        "length": len(content)
                    }, indent=2))]
                    
            except Exception as e:
                return [TextContent(type="text", text=f"Read file error: {e}")]
        
        elif name == "list_todos":
            path_prefix = arguments.get("path_prefix", "")
            
            try:
                import os
                import glob
                import re
                
                todos = []
                search_path = path_prefix if path_prefix else "."
                pattern = f"{search_path}/**/*.py"
                
                todo_patterns = [
                    r'TODO[:\s]*(.+)',
                    r'FIXME[:\s]*(.+)',
                    r'HACK[:\s]*(.+)',
                    r'NOTE[:\s]*(.+)',
                    r'XXX[:\s]*(.+)',
                    r'BUG[:\s]*(.+)'
                ]
                
                for file_path in glob.glob(pattern, recursive=True):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            lines = content.split('\n')
                            
                            for line_num, line in enumerate(lines, 1):
                                for pattern in todo_patterns:
                                    match = re.search(pattern, line, re.IGNORECASE)
                                    if match:
                                        todos.append({
                                            "path": file_path,
                                            "line": line_num,
                                            "text": match.group(1).strip(),
                                            "snippet": line.strip()
                                        })
                    except Exception:
                        continue
                
                return [TextContent(type="text", text=json.dumps({
                    "items": todos,
                    "total": len(todos)
                }, indent=2))]
                
            except Exception as e:
                return [TextContent(type="text", text=f"TODO search error: {e}")]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
    except Exception as e:
        return [TextContent(type="text", text=f"Tool execution error: {e}")]

async def main():
    """Main entry point for the MCP server."""
    try:
        print("Starting CodeCompass MCP Server...", file=sys.stderr)
        
        # Run server
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
            
    except Exception as e:
        print(f"Server error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
