#!/usr/bin/env python3
"""
WhatsApp MCP Server
Provides tools for interacting with WhatsApp through the Model Context Protocol.
"""

import asyncio
import logging
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from mcp.server import Server
from mcp.types import Tool
import json


class WhatsAppMCP:
    def __init__(self):
        self.server = Server("whatsapp-mcp")
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP capability handlers"""

        # Define tools
        send_whatsapp_message_tool = Tool(
            name="send_whatsapp_message",
            description="Send a text message via WhatsApp to a specific contact",
            input_schema={
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
            input_schema={
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

        send_whatsapp_group_message_tool = Tool(
            name="send_whatsapp_group_message",
            description="Send a message to a WhatsApp group",
            input_schema={
                "type": "object",
                "properties": {
                    "group_id": {
                        "type": "string", 
                        "description": "WhatsApp group ID"
                    },
                    "message": {
                        "type": "string", 
                        "description": "Message content to send"
                    }
                },
                "required": ["group_id", "message"]
            }
        )

        get_whatsapp_contacts_tool = Tool(
            name="get_whatsapp_contacts",
            description="Get list of contacts from WhatsApp account",
            input_schema={
                "type": "object",
                "properties": {},
            }
        )

        # Register tools
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                send_whatsapp_message_tool,
                send_whatsapp_media_tool,
                send_whatsapp_group_message_tool,
                get_whatsapp_contacts_tool
            ]

        # Register handlers
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
            if name == "send_whatsapp_message":
                request = WhatsAppMessageRequest(**arguments)
                return [await self.send_whatsapp_message(request)]
            elif name == "send_whatsapp_media":
                request = WhatsAppMediaRequest(**arguments)
                return [await self.send_whatsapp_media(request)]
            elif name == "send_whatsapp_group_message":
                request = WhatsAppGroupRequest(**arguments)
                return [await self.send_whatsapp_group_message(request)]
            elif name == "get_whatsapp_contacts":
                return [await self.get_whatsapp_contacts()]
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def send_whatsapp_message(self, request) -> Dict[str, Any]:
        """
        Send a WhatsApp message to a contact.
        
        Args:
            request: Contains phone number and message content
            
        Returns:
            Dict with success status and message ID
        """
        logger.info(f"Sending WhatsApp message to {request.phone_number}: {request.message}")
        
        # In a real implementation, this would connect to WhatsApp Business API or similar
        # For now, we'll simulate the operation
        await asyncio.sleep(0.1)  # Simulate API call
        
        # Log the action for debugging
        result = {
            "success": True,
            "phone_number": request.phone_number,
            "message_sent": request.message,
            "timestamp": asyncio.get_event_loop().time(),
            "message_id": f"wa_msg_{hash(request.phone_number + request.message) % 10000:04d}"
        }
        
        logger.info(f"WhatsApp message sent successfully: {result['message_id']}")
        return result

    async def send_whatsapp_media(self, request) -> Dict[str, Any]:
        """
        Send media via WhatsApp to a contact.
        
        Args:
            request: Contains phone number, media URL, and optional caption
            
        Returns:
            Dict with success status and media ID
        """
        logger.info(f"Sending WhatsApp media to {request.phone_number}: {request.media_url}")
        
        # In a real implementation, this would upload and send the media
        await asyncio.sleep(0.2)  # Simulate API call
        
        result = {
            "success": True,
            "phone_number": request.phone_number,
            "media_url": request.media_url,
            "caption": request.caption,
            "timestamp": asyncio.get_event_loop().time(),
            "media_id": f"wa_media_{hash(request.phone_number + request.media_url) % 10000:04d}"
        }
        
        logger.info(f"WhatsApp media sent successfully: {result['media_id']}")
        return result

    async def send_whatsapp_group_message(self, request) -> Dict[str, Any]:
        """
        Send a message to a WhatsApp group.
        
        Args:
            request: Contains group ID and message content
            
        Returns:
            Dict with success status and message ID
        """
        logger.info(f"Sending WhatsApp message to group {request.group_id}: {request.message}")
        
        # In a real implementation, this would connect to WhatsApp Business API
        await asyncio.sleep(0.1)  # Simulate API call
        
        result = {
            "success": True,
            "group_id": request.group_id,
            "message_sent": request.message,
            "timestamp": asyncio.get_event_loop().time(),
            "message_id": f"wa_grp_{hash(request.group_id + request.message) % 10000:04d}"
        }
        
        logger.info(f"WhatsApp group message sent successfully: {result['message_id']}")
        return result

    async def get_whatsapp_contacts(self) -> Dict[str, Any]:
        """
        Retrieve contacts from the WhatsApp account.
        
        Returns:
            Dict with list of contacts
        """
        logger.info("Retrieving WhatsApp contacts")
        
        # In a real implementation, this would fetch contacts from the API
        await asyncio.sleep(0.1)  # Simulate API call
        
        contacts = [
            {"name": "John Doe", "phone": "+1234567890", "status": "active"},
            {"name": "Jane Smith", "phone": "+0987654321", "status": "active"},
            {"name": "Business Partner", "phone": "+1122334455", "status": "active"}
        ]
        
        result = {
            "success": True,
            "contacts": contacts,
            "total_count": len(contacts)
        }
        
        logger.info(f"Retrieved {len(contacts)} contacts")
        return result

    async def run(self):
        """Run the WhatsApp MCP server"""
        from mcp.server.stdio import stdio_server
        async with stdio_server(self.server) as make_session:
            async for session in make_session():
                # Keep the server running
                await session.until_closed()


class WhatsAppMessageRequest(BaseModel):
    """Request to send a WhatsApp message."""
    phone_number: str = Field(..., description="Recipient's phone number in international format (e.g., +1234567890)")
    message: str = Field(..., description="Message content to send")


class WhatsAppMediaRequest(BaseModel):
    """Request to send media via WhatsApp."""
    phone_number: str = Field(..., description="Recipient's phone number in international format")
    media_url: str = Field(..., description="URL to the media file to send")
    caption: str = Field(default="", description="Optional caption for the media")


class WhatsAppGroupRequest(BaseModel):
    """Request to send a message to a WhatsApp group."""
    group_id: str = Field(..., description="WhatsApp group ID")
    message: str = Field(..., description="Message content to send")


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Entry point for running the server
async def serve():
    """Run the WhatsApp MCP server."""
    server = WhatsAppMCP()
    await server.run()


if __name__ == "__main__":
    asyncio.run(serve())