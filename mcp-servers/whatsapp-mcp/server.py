#!/usr/bin/env python3
"""
WhatsApp MCP Server
Provides tools for interacting with WhatsApp Business Cloud API
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
WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')
WHATSAPP_BUSINESS_ACCOUNT_ID = os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID', '')
DRY_RUN = os.getenv('DRY_RUN', 'false').lower() == 'true'
GRAPH_API_BASE = 'https://graph.facebook.com/v18.0'


class WhatsAppMCP:
    def __init__(self):
        self.server = Server("whatsapp-mcp")
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP capability handlers"""

        send_whatsapp_message_tool = Tool(
            name="send_whatsapp_message",
            description="Send a text message via WhatsApp Business API to a specific contact",
            inputSchema={
                "type": "object",
                "properties": {
                    "phone_number": {
                        "type": "string",
                        "description": "Recipient's phone number in international format (e.g., +1234567890)"
                    },
                    "message": {
                        "type": "string",
                        "description": "Message content to send"
                    }
                },
                "required": ["phone_number", "message"]
            }
        )

        send_whatsapp_media_tool = Tool(
            name="send_whatsapp_media",
            description="Send media (image, video, document) via WhatsApp to a specific contact",
            inputSchema={
                "type": "object",
                "properties": {
                    "phone_number": {
                        "type": "string",
                        "description": "Recipient's phone number in international format"
                    },
                    "media_url": {
                        "type": "string",
                        "description": "URL to the media file to send"
                    },
                    "caption": {
                        "type": "string",
                        "description": "Optional caption for the media",
                        "default": ""
                    }
                },
                "required": ["phone_number", "media_url"]
            }
        )

        send_whatsapp_template_tool = Tool(
            name="send_whatsapp_template",
            description="Send a WhatsApp template message (approved templates only)",
            inputSchema={
                "type": "object",
                "properties": {
                    "phone_number": {
                        "type": "string",
                        "description": "Recipient's phone number in international format"
                    },
                    "template_name": {
                        "type": "string",
                        "description": "Name of the approved template to use"
                    },
                    "language_code": {
                        "type": "string",
                        "description": "Language code (e.g., en_US)",
                        "default": "en_US"
                    }
                },
                "required": ["phone_number", "template_name"]
            }
        )

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                send_whatsapp_message_tool,
                send_whatsapp_media_tool,
                send_whatsapp_template_tool,
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
            if name == "send_whatsapp_message":
                request = WhatsAppMessageRequest(**arguments)
                return [await self.send_whatsapp_message(request)]
            elif name == "send_whatsapp_media":
                request = WhatsAppMediaRequest(**arguments)
                return [await self.send_whatsapp_media(request)]
            elif name == "send_whatsapp_template":
                request = WhatsAppTemplateRequest(**arguments)
                return [await self.send_whatsapp_template(request)]
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def send_whatsapp_message(self, request) -> Dict[str, Any]:
        """Send a WhatsApp text message via Meta Cloud API."""
        logger.info(f"Sending WhatsApp message to {request.phone_number}")

        if DRY_RUN:
            logger.info(f"[DRY RUN] Would send: '{request.message}' to {request.phone_number}")
            return {
                "success": True,
                "dry_run": True,
                "phone_number": request.phone_number,
                "message": request.message,
                "timestamp": datetime.now().isoformat()
            }

        if not WHATSAPP_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
            return {"success": False, "error": "WHATSAPP_ACCESS_TOKEN or WHATSAPP_PHONE_NUMBER_ID not configured"}

        # Normalize phone number — strip leading + if present for Meta API
        to_number = request.phone_number.lstrip('+')

        url = f"{GRAPH_API_BASE}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "text",
            "text": {"preview_url": False, "body": request.message}
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            data = response.json()

            if response.status_code == 200:
                msg_id = data.get('messages', [{}])[0].get('id', 'unknown')
                logger.info(f"WhatsApp message sent: {msg_id}")
                return {
                    "success": True,
                    "message_id": msg_id,
                    "phone_number": request.phone_number,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                error_msg = data.get('error', {}).get('message', response.text)
                logger.error(f"WhatsApp API error {response.status_code}: {error_msg}")
                return {"success": False, "error": error_msg, "status_code": response.status_code}

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error sending WhatsApp message: {e}")
            return {"success": False, "error": str(e)}

    async def send_whatsapp_media(self, request) -> Dict[str, Any]:
        """Send media via WhatsApp Business API."""
        logger.info(f"Sending WhatsApp media to {request.phone_number}: {request.media_url}")

        if DRY_RUN:
            logger.info(f"[DRY RUN] Would send media to {request.phone_number}")
            return {
                "success": True,
                "dry_run": True,
                "phone_number": request.phone_number,
                "media_url": request.media_url,
                "timestamp": datetime.now().isoformat()
            }

        if not WHATSAPP_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
            return {"success": False, "error": "WhatsApp credentials not configured"}

        to_number = request.phone_number.lstrip('+')
        url = f"{GRAPH_API_BASE}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number,
            "type": "image",
            "image": {"link": request.media_url, "caption": request.caption}
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            data = response.json()
            if response.status_code == 200:
                media_id = data.get('messages', [{}])[0].get('id', 'unknown')
                return {"success": True, "media_id": media_id, "timestamp": datetime.now().isoformat()}
            else:
                error_msg = data.get('error', {}).get('message', response.text)
                return {"success": False, "error": error_msg}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    async def send_whatsapp_template(self, request) -> Dict[str, Any]:
        """Send a WhatsApp approved template message."""
        logger.info(f"Sending WhatsApp template '{request.template_name}' to {request.phone_number}")

        if DRY_RUN:
            return {"success": True, "dry_run": True, "template": request.template_name}

        if not WHATSAPP_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
            return {"success": False, "error": "WhatsApp credentials not configured"}

        to_number = request.phone_number.lstrip('+')
        url = f"{GRAPH_API_BASE}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        headers = {
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "template",
            "template": {
                "name": request.template_name,
                "language": {"code": request.language_code}
            }
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            data = response.json()
            if response.status_code == 200:
                msg_id = data.get('messages', [{}])[0].get('id', 'unknown')
                return {"success": True, "message_id": msg_id, "template": request.template_name}
            else:
                error_msg = data.get('error', {}).get('message', response.text)
                return {"success": False, "error": error_msg}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    async def run(self):
        """Run the WhatsApp MCP server via stdio."""
        from mcp.server.stdio import stdio_server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


# --- Pydantic request models ---

class WhatsAppMessageRequest(BaseModel):
    phone_number: str = Field(..., description="Recipient's phone number in international format")
    message: str = Field(..., description="Message content to send")


class WhatsAppMediaRequest(BaseModel):
    phone_number: str = Field(..., description="Recipient's phone number in international format")
    media_url: str = Field(..., description="URL to the media file to send")
    caption: str = Field(default="", description="Optional caption for the media")


class WhatsAppTemplateRequest(BaseModel):
    phone_number: str = Field(..., description="Recipient's phone number in international format")
    template_name: str = Field(..., description="Name of the approved template")
    language_code: str = Field(default="en_US", description="Language code")


async def serve():
    """Entry point for running the WhatsApp MCP server."""
    server = WhatsAppMCP()
    await server.run()


if __name__ == "__main__":
    asyncio.run(serve())
