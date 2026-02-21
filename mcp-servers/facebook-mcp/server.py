#!/usr/bin/env python3
"""
Facebook MCP Server
Provides tools for interacting with Facebook Graph API
through the Model Context Protocol.
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, Any, List

import requests
from pydantic import BaseModel, Field
from mcp.server import Server
from mcp.types import Tool

# Load env from .env file if available
try:
    from dotenv import load_dotenv
    from pathlib import Path
    load_dotenv(Path(__file__).parent.parent.parent / '.env')
except ImportError:
    pass

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Credential loading ---
FACEBOOK_ACCESS_TOKEN = os.getenv('FACEBOOK_ACCESS_TOKEN', '')
FACEBOOK_PAGE_ID = os.getenv('FACEBOOK_PAGE_ID', '')
DRY_RUN = os.getenv('DRY_RUN', 'false').lower() == 'true'
GRAPH_API_BASE = 'https://graph.facebook.com/v18.0'


class FacebookMCP:
    def __init__(self):
        self.server = Server("facebook-mcp")
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP capability handlers"""

        create_facebook_page_post_tool = Tool(
            name="create_facebook_page_post",
            description="Create a post on the configured Facebook Page",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Content of the post"
                    },
                    "link": {
                        "type": "string",
                        "description": "Optional URL to include in the post",
                        "default": ""
                    }
                },
                "required": ["message"]
            }
        )

        get_page_insights_tool = Tool(
            name="get_facebook_page_insights",
            description="Get basic insights for the configured Facebook Page",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )

        get_page_posts_tool = Tool(
            name="get_facebook_page_posts",
            description="Get recent posts from the configured Facebook Page",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of posts to retrieve (max 25)",
                        "default": 5
                    }
                }
            }
        )

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                create_facebook_page_post_tool,
                get_page_insights_tool,
                get_page_posts_tool,
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
            if name == "create_facebook_page_post":
                request = FacebookPagePostRequest(**arguments)
                return [await self.create_facebook_page_post(request)]
            elif name == "get_facebook_page_insights":
                return [await self.get_facebook_page_insights()]
            elif name == "get_facebook_page_posts":
                limit = arguments.get('limit', 5)
                return [await self.get_facebook_page_posts(limit)]
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def create_facebook_page_post(self, request) -> Dict[str, Any]:
        """Post to Facebook Page using Graph API."""
        logger.info(f"Creating Facebook page post: {request.message[:60]}...")

        if DRY_RUN:
            logger.info(f"[DRY RUN] Would post to Facebook page {FACEBOOK_PAGE_ID}: '{request.message[:80]}'")
            return {
                "success": True,
                "dry_run": True,
                "page_id": FACEBOOK_PAGE_ID,
                "message": request.message,
                "timestamp": datetime.now().isoformat()
            }

        if not FACEBOOK_ACCESS_TOKEN:
            return {"success": False, "error": "FACEBOOK_ACCESS_TOKEN not configured"}

        if not FACEBOOK_PAGE_ID:
            return {"success": False, "error": "FACEBOOK_PAGE_ID not configured in .env"}

        url = f"{GRAPH_API_BASE}/{FACEBOOK_PAGE_ID}/feed"
        payload = {
            "message": request.message,
            "access_token": FACEBOOK_ACCESS_TOKEN
        }
        if request.link:
            payload["link"] = request.link

        try:
            response = requests.post(url, data=payload, timeout=30)
            data = response.json()

            if response.status_code == 200 and 'id' in data:
                post_id = data['id']
                logger.info(f"Facebook post created: {post_id}")
                return {
                    "success": True,
                    "post_id": post_id,
                    "page_id": FACEBOOK_PAGE_ID,
                    "url": f"https://www.facebook.com/{post_id}",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                error_msg = data.get('error', {}).get('message', response.text)
                logger.error(f"Facebook API error {response.status_code}: {error_msg}")
                return {"success": False, "error": error_msg, "status_code": response.status_code}

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error posting to Facebook: {e}")
            return {"success": False, "error": str(e)}

    async def get_facebook_page_insights(self) -> Dict[str, Any]:
        """Get basic page insights (fans, engagement)."""
        logger.info("Retrieving Facebook page insights")

        if not FACEBOOK_ACCESS_TOKEN or not FACEBOOK_PAGE_ID:
            return {"success": False, "error": "Facebook credentials not configured"}

        url = f"{GRAPH_API_BASE}/{FACEBOOK_PAGE_ID}"
        params = {
            "fields": "name,fan_count,followers_count,talking_about_count",
            "access_token": FACEBOOK_ACCESS_TOKEN
        }

        try:
            response = requests.get(url, params=params, timeout=15)
            data = response.json()

            if response.status_code == 200:
                return {
                    "success": True,
                    "page_name": data.get('name', ''),
                    "fans": data.get('fan_count', 0),
                    "followers": data.get('followers_count', 0),
                    "talking_about": data.get('talking_about_count', 0),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"success": False, "error": data.get('error', {}).get('message', response.text)}

        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    async def get_facebook_page_posts(self, limit: int = 5) -> Dict[str, Any]:
        """Get recent posts from the configured Facebook Page."""
        logger.info(f"Retrieving {limit} recent Facebook page posts")

        if not FACEBOOK_ACCESS_TOKEN or not FACEBOOK_PAGE_ID:
            return {"success": False, "error": "Facebook credentials not configured"}

        url = f"{GRAPH_API_BASE}/{FACEBOOK_PAGE_ID}/posts"
        params = {
            "fields": "id,message,created_time,story",
            "limit": min(limit, 25),
            "access_token": FACEBOOK_ACCESS_TOKEN
        }

        try:
            response = requests.get(url, params=params, timeout=15)
            data = response.json()

            if response.status_code == 200:
                posts = data.get('data', [])
                return {
                    "success": True,
                    "posts": posts,
                    "count": len(posts),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"success": False, "error": data.get('error', {}).get('message', response.text)}

        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    async def run(self):
        """Run the Facebook MCP server via stdio."""
        from mcp.server.stdio import stdio_server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


# --- Pydantic request models ---

class FacebookPagePostRequest(BaseModel):
    message: str = Field(..., description="Content of the post")
    link: str = Field(default="", description="Optional URL to include")


async def serve():
    """Entry point for running the Facebook MCP server."""
    server = FacebookMCP()
    await server.run()


if __name__ == "__main__":
    asyncio.run(serve())
