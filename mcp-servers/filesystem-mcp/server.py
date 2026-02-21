"""
Filesystem MCP Server for AI Employee
Provides file system operations through Model Context Protocol
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from mcp.server import Server
from mcp.types import Notification, Prompt, PromptResult, Tool
import aiofiles


class FilesystemMCP:
    def __init__(self):
        self.server = Server("filesystem-mcp")
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP capability handlers"""
        
        # Define tools
        read_file_tool = Tool(
            name="read_file",
            description="Read the contents of a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file to read"}
                },
                "required": ["path"]
            }
        )
        
        write_file_tool = Tool(
            name="write_file",
            description="Write content to a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file to write"},
                    "content": {"type": "string", "description": "Content to write to the file"}
                },
                "required": ["path", "content"]
            }
        )
        
        list_directory_tool = Tool(
            name="list_directory",
            description="List files and directories in a given path",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to list"}
                },
                "required": ["path"]
            }
        )
        
        create_directory_tool = Tool(
            name="create_directory",
            description="Create a new directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path of the directory to create"}
                },
                "required": ["path"]
            }
        )
        
        # Register tools
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                read_file_tool,
                write_file_tool,
                list_directory_tool,
                create_directory_tool
            ]

        # Register handlers
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
            if name == "read_file":
                return [await self.read_file(arguments["path"])]
            elif name == "write_file":
                return [await self.write_file(arguments["path"], arguments["content"])]
            elif name == "list_directory":
                return [await self.list_directory(arguments["path"])]
            elif name == "create_directory":
                return [await self.create_directory(arguments["path"])]
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def read_file(self, path: str) -> Dict[str, Any]:
        """Read the contents of a file"""
        try:
            file_path = Path(path)
            if not file_path.exists():
                return {"error": f"File does not exist: {path}"}
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            return {
                "success": True,
                "path": str(file_path),
                "content": content,
                "size": len(content)
            }
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}

    async def write_file(self, path: str, content: str) -> Dict[str, Any]:
        """Write content to a file"""
        try:
            file_path = Path(path)
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            return {
                "success": True,
                "path": str(file_path),
                "written_bytes": len(content)
            }
        except Exception as e:
            return {"error": f"Failed to write file: {str(e)}"}

    async def list_directory(self, path: str) -> Dict[str, Any]:
        """List files and directories in a given path"""
        try:
            dir_path = Path(path)
            if not dir_path.exists() or not dir_path.is_dir():
                return {"error": f"Directory does not exist or is not a directory: {path}"}
            
            items = []
            for item in dir_path.iterdir():
                item_info = {
                    "name": item.name,
                    "path": str(item),
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else 0
                }
                items.append(item_info)
            
            return {
                "success": True,
                "path": str(dir_path),
                "items": items,
                "count": len(items)
            }
        except Exception as e:
            return {"error": f"Failed to list directory: {str(e)}"}

    async def create_directory(self, path: str) -> Dict[str, Any]:
        """Create a new directory"""
        try:
            dir_path = Path(path)
            dir_path.mkdir(parents=True, exist_ok=True)
            
            return {
                "success": True,
                "path": str(dir_path)
            }
        except Exception as e:
            return {"error": f"Failed to create directory: {str(e)}"}

    async def run(self):
        """Run the filesystem MCP server"""
        from mcp.server.stdio import stdio_server
        async with stdio_server(self.server) as make_session:
            async for session in make_session():
                # Keep the server running
                await session.until_closed()


# Entry point
async def main():
    server = FilesystemMCP()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())