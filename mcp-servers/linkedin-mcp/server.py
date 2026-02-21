#!/usr/bin/env python3
"""
LinkedIn MCP Server
Provides tools for interacting with LinkedIn API v2
through the Model Context Protocol.
"""

import asyncio
import logging
import os
import json
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
LINKEDIN_ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN', '')
LINKEDIN_PAGE_ID = os.getenv('LINKEDIN_PAGE_ID', '')
DRY_RUN = os.getenv('DRY_RUN', 'false').lower() == 'true'
LINKEDIN_API_BASE = 'https://api.linkedin.com/v2'


def _linkedin_headers() -> dict:
    return {
        'Authorization': f'Bearer {LINKEDIN_ACCESS_TOKEN}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }


def _get_person_urn() -> str:
    """Retrieve authenticated user's URN from LinkedIn."""
    try:
        response = requests.get(
            f'{LINKEDIN_API_BASE}/userinfo',
            headers=_linkedin_headers(),
            timeout=15
        )
        if response.status_code == 200:
            sub = response.json().get('sub', '')
            return f'urn:li:person:{sub}'
    except Exception as e:
        logger.error(f"Could not retrieve person URN: {e}")
    return ''


class LinkedInMCP:
    def __init__(self):
        self.server = Server("linkedin-mcp")
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP capability handlers"""

        create_linkedin_post_tool = Tool(
            name="create_linkedin_post",
            description="Create a post on the authenticated LinkedIn account (personal feed)",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Content of the post"
                    },
                    "visibility": {
                        "type": "string",
                        "description": "Visibility: PUBLIC or CONNECTIONS",
                        "default": "PUBLIC"
                    }
                },
                "required": ["text"]
            }
        )

        create_linkedin_page_post_tool = Tool(
            name="create_linkedin_page_post",
            description="Create a post on a LinkedIn Company Page",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Content of the post"
                    },
                    "visibility": {
                        "type": "string",
                        "description": "Visibility: PUBLIC or CONNECTIONS",
                        "default": "PUBLIC"
                    }
                },
                "required": ["text"]
            }
        )

        get_profile_tool = Tool(
            name="get_linkedin_profile",
            description="Get the authenticated LinkedIn user's profile info",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                create_linkedin_post_tool,
                create_linkedin_page_post_tool,
                get_profile_tool,
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
            if name == "create_linkedin_post":
                request = LinkedInPostRequest(**arguments)
                return [await self.create_linkedin_post(request)]
            elif name == "create_linkedin_page_post":
                request = LinkedInPostRequest(**arguments)
                return [await self.create_linkedin_page_post(request)]
            elif name == "get_linkedin_profile":
                return [await self.get_linkedin_profile()]
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def create_linkedin_post(self, request) -> Dict[str, Any]:
        """Create a personal LinkedIn post using UGC Posts API."""
        logger.info(f"Creating LinkedIn personal post: {request.text[:60]}...")

        if DRY_RUN:
            logger.info(f"[DRY RUN] Would post to LinkedIn: '{request.text[:80]}...'")
            return {
                "success": True,
                "dry_run": True,
                "text": request.text,
                "timestamp": datetime.now().isoformat()
            }

        if not LINKEDIN_ACCESS_TOKEN:
            return {"success": False, "error": "LINKEDIN_ACCESS_TOKEN not configured"}

        # Get person URN
        person_urn = _get_person_urn()
        if not person_urn:
            return {"success": False, "error": "Could not retrieve LinkedIn person URN — check access token"}

        visibility_map = {
            "PUBLIC": "PUBLIC",
            "CONNECTIONS": "CONNECTIONS_ONLY"
        }
        visibility = visibility_map.get(request.visibility.upper(), "PUBLIC")

        payload = {
            "author": person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": request.text},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": visibility
            }
        }

        try:
            response = requests.post(
                f'{LINKEDIN_API_BASE}/ugcPosts',
                json=payload,
                headers=_linkedin_headers(),
                timeout=30
            )

            if response.status_code in (200, 201):
                post_id = response.headers.get('x-restli-id', response.json().get('id', 'unknown'))
                logger.info(f"LinkedIn post created: {post_id}")
                return {
                    "success": True,
                    "post_id": post_id,
                    "visibility": visibility,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                error_msg = response.text
                logger.error(f"LinkedIn API error {response.status_code}: {error_msg}")
                return {"success": False, "error": error_msg, "status_code": response.status_code}

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error creating LinkedIn post: {e}")
            return {"success": False, "error": str(e)}

    async def create_linkedin_page_post(self, request) -> Dict[str, Any]:
        """Create a post on a LinkedIn Company Page."""
        logger.info(f"Creating LinkedIn page post: {request.text[:60]}...")

        if DRY_RUN:
            return {"success": True, "dry_run": True, "page_id": LINKEDIN_PAGE_ID, "timestamp": datetime.now().isoformat()}

        if not LINKEDIN_ACCESS_TOKEN:
            return {"success": False, "error": "LINKEDIN_ACCESS_TOKEN not configured"}

        if not LINKEDIN_PAGE_ID:
            return {"success": False, "error": "LINKEDIN_PAGE_ID not configured in .env"}

        org_urn = f"urn:li:organization:{LINKEDIN_PAGE_ID}"

        payload = {
            "author": org_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": request.text},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        try:
            response = requests.post(
                f'{LINKEDIN_API_BASE}/ugcPosts',
                json=payload,
                headers=_linkedin_headers(),
                timeout=30
            )

            if response.status_code in (200, 201):
                post_id = response.headers.get('x-restli-id', 'unknown')
                logger.info(f"LinkedIn page post created: {post_id}")
                return {
                    "success": True,
                    "post_id": post_id,
                    "page_id": LINKEDIN_PAGE_ID,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"success": False, "error": response.text, "status_code": response.status_code}

        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    async def get_linkedin_profile(self) -> Dict[str, Any]:
        """Get authenticated LinkedIn user profile."""
        logger.info("Retrieving LinkedIn profile")

        if not LINKEDIN_ACCESS_TOKEN:
            return {"success": False, "error": "LINKEDIN_ACCESS_TOKEN not configured"}

        try:
            response = requests.get(
                f'{LINKEDIN_API_BASE}/userinfo',
                headers=_linkedin_headers(),
                timeout=15
            )

            if response.status_code == 200:
                profile = response.json()
                return {
                    "success": True,
                    "name": profile.get('name', ''),
                    "email": profile.get('email', ''),
                    "sub": profile.get('sub', ''),
                    "picture": profile.get('picture', '')
                }
            else:
                return {"success": False, "error": response.text}

        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    async def run(self):
        """Run the LinkedIn MCP server via stdio."""
        from mcp.server.stdio import stdio_server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


# --- Pydantic request models ---

class LinkedInPostRequest(BaseModel):
    text: str = Field(..., description="Content of the post")
    visibility: str = Field(default="PUBLIC", description="Visibility: PUBLIC or CONNECTIONS")


async def serve():
    """Entry point for running the LinkedIn MCP server."""
    server = LinkedInMCP()
    await server.run()


if __name__ == "__main__":
    asyncio.run(serve())
