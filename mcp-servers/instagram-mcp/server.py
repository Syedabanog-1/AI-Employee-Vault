#!/usr/bin/env python3
"""
Instagram MCP Server
Provides tools for interacting with Instagram Graph API (Business)
through the Model Context Protocol.

REQUIREMENTS:
- INSTAGRAM_ACCESS_TOKEN: Meta access token with instagram_basic + instagram_content_publish scope
- INSTAGRAM_ACCOUNT_ID: Instagram Business Account ID (NOT Facebook Page ID)
  Retrieve it once: GET /{fb-page-id}?fields=instagram_business_account&access_token={token}
  Then add INSTAGRAM_ACCOUNT_ID=<value> to .env
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
INSTAGRAM_ACCESS_TOKEN = os.getenv('INSTAGRAM_ACCESS_TOKEN', '')
INSTAGRAM_ACCOUNT_ID = os.getenv('INSTAGRAM_ACCOUNT_ID', '')
DRY_RUN = os.getenv('DRY_RUN', 'false').lower() == 'true'
GRAPH_API_BASE = 'https://graph.facebook.com/v18.0'


class InstagramMCP:
    def __init__(self):
        self.server = Server("instagram-mcp")
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP capability handlers"""

        create_instagram_post_tool = Tool(
            name="create_instagram_post",
            description="Create an image post on the Instagram Business account (requires public image URL)",
            inputSchema={
                "type": "object",
                "properties": {
                    "image_url": {
                        "type": "string",
                        "description": "Publicly accessible URL to the image"
                    },
                    "caption": {
                        "type": "string",
                        "description": "Caption for the post",
                        "default": ""
                    }
                },
                "required": ["image_url"]
            }
        )

        create_instagram_text_post_tool = Tool(
            name="create_instagram_text_post",
            description="Create a text-only (carousel placeholder) post — Note: Instagram requires an image; this posts a caption with a placeholder",
            inputSchema={
                "type": "object",
                "properties": {
                    "caption": {
                        "type": "string",
                        "description": "Caption/text content for the post"
                    },
                    "image_url": {
                        "type": "string",
                        "description": "Optional background image URL (recommended)",
                        "default": ""
                    }
                },
                "required": ["caption"]
            }
        )

        get_instagram_profile_tool = Tool(
            name="get_instagram_profile",
            description="Get the Instagram Business account profile info",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )

        get_instagram_insights_tool = Tool(
            name="get_instagram_insights",
            description="Get basic Instagram account insights (followers, media count)",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                create_instagram_post_tool,
                create_instagram_text_post_tool,
                get_instagram_profile_tool,
                get_instagram_insights_tool,
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
            if name == "create_instagram_post":
                request = InstagramPostRequest(**arguments)
                return [await self.create_instagram_post(request)]
            elif name == "create_instagram_text_post":
                request = InstagramTextPostRequest(**arguments)
                return [await self.create_instagram_text_post(request)]
            elif name == "get_instagram_profile":
                return [await self.get_instagram_profile()]
            elif name == "get_instagram_insights":
                return [await self.get_instagram_insights()]
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def _create_media_container(self, image_url: str, caption: str) -> str:
        """Step 1: Create Instagram media container. Returns container ID or empty string on failure."""
        url = f"{GRAPH_API_BASE}/{INSTAGRAM_ACCOUNT_ID}/media"
        payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": INSTAGRAM_ACCESS_TOKEN
        }
        response = requests.post(url, data=payload, timeout=30)
        data = response.json()

        if response.status_code == 200 and 'id' in data:
            logger.info(f"Media container created: {data['id']}")
            return data['id']
        else:
            error_msg = data.get('error', {}).get('message', response.text)
            logger.error(f"Failed to create media container: {error_msg}")
            return ''

    async def _publish_media_container(self, container_id: str) -> Dict[str, Any]:
        """Step 2: Publish the Instagram media container."""
        url = f"{GRAPH_API_BASE}/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        payload = {
            "creation_id": container_id,
            "access_token": INSTAGRAM_ACCESS_TOKEN
        }
        response = requests.post(url, data=payload, timeout=30)
        data = response.json()

        if response.status_code == 200 and 'id' in data:
            post_id = data['id']
            logger.info(f"Instagram post published: {post_id}")
            return {
                "success": True,
                "post_id": post_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            error_msg = data.get('error', {}).get('message', response.text)
            logger.error(f"Failed to publish Instagram post: {error_msg}")
            return {"success": False, "error": error_msg}

    async def create_instagram_post(self, request) -> Dict[str, Any]:
        """Create an Instagram post via two-step media container + publish flow."""
        logger.info(f"Creating Instagram post with image: {request.image_url}")

        if DRY_RUN:
            logger.info(f"[DRY RUN] Would post to Instagram with caption: '{request.caption[:80]}'")
            return {
                "success": True,
                "dry_run": True,
                "image_url": request.image_url,
                "caption": request.caption,
                "timestamp": datetime.now().isoformat()
            }

        if not INSTAGRAM_ACCESS_TOKEN:
            return {"success": False, "error": "INSTAGRAM_ACCESS_TOKEN not configured"}

        if not INSTAGRAM_ACCOUNT_ID:
            return {
                "success": False,
                "error": (
                    "INSTAGRAM_ACCOUNT_ID not configured in .env. "
                    "Retrieve it by calling: "
                    f"GET https://graph.facebook.com/v18.0/{{FACEBOOK_PAGE_ID}}"
                    "?fields=instagram_business_account&access_token={FACEBOOK_ACCESS_TOKEN}"
                )
            }

        try:
            # Step 1: Create container
            container_id = await self._create_media_container(request.image_url, request.caption)
            if not container_id:
                return {"success": False, "error": "Failed to create media container"}

            # Step 2: Publish
            result = await self._publish_media_container(container_id)
            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error creating Instagram post: {e}")
            return {"success": False, "error": str(e)}

    async def create_instagram_text_post(self, request) -> Dict[str, Any]:
        """Create an Instagram post with a caption. An image URL is required by Instagram API."""
        logger.info(f"Creating Instagram text post: {request.caption[:60]}...")

        if DRY_RUN:
            return {
                "success": True,
                "dry_run": True,
                "caption": request.caption,
                "timestamp": datetime.now().isoformat()
            }

        if not request.image_url:
            return {
                "success": False,
                "error": "Instagram requires an image_url — provide a publicly accessible image URL along with your caption"
            }

        # Delegate to create_instagram_post with the provided image
        post_request = InstagramPostRequest(image_url=request.image_url, caption=request.caption)
        return await self.create_instagram_post(post_request)

    async def get_instagram_profile(self) -> Dict[str, Any]:
        """Get Instagram Business account profile."""
        logger.info("Retrieving Instagram profile")

        if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
            return {"success": False, "error": "Instagram credentials not configured"}

        url = f"{GRAPH_API_BASE}/{INSTAGRAM_ACCOUNT_ID}"
        params = {
            "fields": "id,name,username,biography,followers_count,media_count,profile_picture_url",
            "access_token": INSTAGRAM_ACCESS_TOKEN
        }

        try:
            response = requests.get(url, params=params, timeout=15)
            data = response.json()

            if response.status_code == 200:
                return {
                    "success": True,
                    "id": data.get('id', ''),
                    "name": data.get('name', ''),
                    "username": data.get('username', ''),
                    "biography": data.get('biography', ''),
                    "followers_count": data.get('followers_count', 0),
                    "media_count": data.get('media_count', 0),
                    "profile_picture_url": data.get('profile_picture_url', ''),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"success": False, "error": data.get('error', {}).get('message', response.text)}

        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    async def get_instagram_insights(self) -> Dict[str, Any]:
        """Get Instagram account-level insights."""
        logger.info("Retrieving Instagram insights")

        if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
            return {"success": False, "error": "Instagram credentials not configured"}

        url = f"{GRAPH_API_BASE}/{INSTAGRAM_ACCOUNT_ID}/insights"
        params = {
            "metric": "impressions,reach,profile_views",
            "period": "day",
            "access_token": INSTAGRAM_ACCESS_TOKEN
        }

        try:
            response = requests.get(url, params=params, timeout=15)
            data = response.json()

            if response.status_code == 200:
                insights = {item['name']: item['values'][-1]['value'] for item in data.get('data', [])}
                return {"success": True, "insights": insights, "timestamp": datetime.now().isoformat()}
            else:
                return {"success": False, "error": data.get('error', {}).get('message', response.text)}

        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    async def run(self):
        """Run the Instagram MCP server via stdio."""
        from mcp.server.stdio import stdio_server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


# --- Pydantic request models ---

class InstagramPostRequest(BaseModel):
    image_url: str = Field(..., description="Publicly accessible URL to the image")
    caption: str = Field(default="", description="Caption for the post")


class InstagramTextPostRequest(BaseModel):
    caption: str = Field(..., description="Caption/text content for the post")
    image_url: str = Field(default="", description="Optional background image URL")


async def serve():
    """Entry point for running the Instagram MCP server."""
    server = InstagramMCP()
    await server.run()


if __name__ == "__main__":
    asyncio.run(serve())
