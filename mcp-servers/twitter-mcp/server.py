#!/usr/bin/env python3
"""
Twitter MCP Server
Provides tools for interacting with Twitter through the Model Context Protocol.
"""

import asyncio
import logging
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from mcp.server import Server
from mcp.types import Tool
import json


class TwitterMCP:
    def __init__(self):
        self.server = Server("twitter-mcp")
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP capability handlers"""

        # Define tools
        create_twitter_post_tool = Tool(
            name="create_twitter_post",
            description="Create a tweet on the authenticated Twitter account",
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string", 
                        "description": "Content of the tweet (max 280 characters)"
                    },
                    "media_url": {
                        "type": "string", 
                        "description": "Optional URL to media to attach to the tweet",
                        "default": ""
                    }
                },
                "required": ["text"]
            }
        )

        create_twitter_thread_tool = Tool(
            name="create_twitter_thread",
            description="Create a thread of tweets on the authenticated Twitter account",
            input_schema={
                "type": "object",
                "properties": {
                    "tweets": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of tweet texts in the thread"
                    }
                },
                "required": ["tweets"]
            }
        )

        reply_to_tweet_tool = Tool(
            name="reply_to_tweet",
            description="Reply to an existing tweet",
            input_schema={
                "type": "object",
                "properties": {
                    "tweet_id": {
                        "type": "string", 
                        "description": "ID of the tweet to reply to"
                    },
                    "text": {
                        "type": "string", 
                        "description": "Content of the reply"
                    }
                },
                "required": ["tweet_id", "text"]
            }
        )

        send_twitter_message_tool = Tool(
            name="send_twitter_message",
            description="Send a direct message to a Twitter user",
            input_schema={
                "type": "object",
                "properties": {
                    "recipient_username": {
                        "type": "string", 
                        "description": "Username of the recipient"
                    },
                    "text": {
                        "type": "string", 
                        "description": "Message content to send"
                    }
                },
                "required": ["recipient_username", "text"]
            }
        )

        like_tweet_tool = Tool(
            name="like_tweet",
            description="Like an existing tweet",
            input_schema={
                "type": "object",
                "properties": {
                    "tweet_id": {
                        "type": "string", 
                        "description": "ID of the tweet to like"
                    }
                },
                "required": ["tweet_id"]
            }
        )

        get_twitter_followers_tool = Tool(
            name="get_twitter_followers",
            description="Get list of Twitter followers",
            input_schema={
                "type": "object",
                "properties": {},
            }
        )

        # Register tools
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                create_twitter_post_tool,
                create_twitter_thread_tool,
                reply_to_tweet_tool,
                send_twitter_message_tool,
                like_tweet_tool,
                get_twitter_followers_tool
            ]

        # Register handlers
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
            if name == "create_twitter_post":
                request = TwitterPostRequest(**arguments)
                return [await self.create_twitter_post(request)]
            elif name == "create_twitter_thread":
                request = TwitterThreadRequest(**arguments)
                return [await self.create_twitter_thread(request)]
            elif name == "reply_to_tweet":
                request = TwitterReplyRequest(**arguments)
                return [await self.reply_to_tweet(request)]
            elif name == "send_twitter_message":
                request = TwitterMessageRequest(**arguments)
                return [await self.send_twitter_message(request)]
            elif name == "like_tweet":
                request = TwitterLikeRequest(**arguments)
                return [await self.like_tweet(request)]
            elif name == "get_twitter_followers":
                return [await self.get_twitter_followers()]
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def create_twitter_post(self, request) -> Dict[str, Any]:
        """
        Create a Twitter post (tweet).
        
        Args:
            request: Contains tweet text and optional media URL
            
        Returns:
            Dict with success status and tweet ID
        """
        logger.info(f"Creating Twitter post: {request.text[:50]}...")
        
        # In a real implementation, this would connect to Twitter API
        await asyncio.sleep(0.1)  # Simulate API call
        
        result = {
            "success": True,
            "text": request.text,
            "has_media": bool(request.media_url),
            "timestamp": asyncio.get_event_loop().time(),
            "tweet_id": f"tw_post_{hash(request.text) % 10000:04d}"
        }
        
        logger.info(f"Twitter post created successfully: {result['tweet_id']}")
        return result

    async def create_twitter_thread(self, request) -> Dict[str, Any]:
        """
        Create a Twitter thread (series of tweets).
        
        Args:
            request: Contains list of tweet texts
            
        Returns:
            Dict with success status and list of tweet IDs
        """
        logger.info(f"Creating Twitter thread with {len(request.tweets)} tweets")
        
        # In a real implementation, this would connect to Twitter API
        await asyncio.sleep(0.2)  # Simulate API call
        
        tweet_ids = [f"tw_thread_{i}_{hash(tweet) % 10000:04d}" for i, tweet in enumerate(request.tweets)]
        
        result = {
            "success": True,
            "tweet_count": len(request.tweets),
            "tweet_ids": tweet_ids,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        logger.info(f"Twitter thread created successfully with {len(tweet_ids)} tweets")
        return result

    async def reply_to_tweet(self, request) -> Dict[str, Any]:
        """
        Reply to a Twitter post.
        
        Args:
            request: Contains tweet ID to reply to and reply text
            
        Returns:
            Dict with success status and reply tweet ID
        """
        logger.info(f"Replying to tweet {request.tweet_id}: {request.text[:50]}...")
        
        # In a real implementation, this would connect to Twitter API
        await asyncio.sleep(0.1)  # Simulate API call
        
        result = {
            "success": True,
            "original_tweet_id": request.tweet_id,
            "reply_text": request.text,
            "timestamp": asyncio.get_event_loop().time(),
            "reply_tweet_id": f"tw_reply_{hash(request.tweet_id + request.text) % 10000:04d}"
        }
        
        logger.info(f"Twitter reply posted successfully: {result['reply_tweet_id']}")
        return result

    async def send_twitter_message(self, request) -> Dict[str, Any]:
        """
        Send a Twitter direct message.
        
        Args:
            request: Contains recipient username and message text
            
        Returns:
            Dict with success status and message ID
        """
        logger.info(f"Sending Twitter DM to {request.recipient_username}: {request.text[:50]}...")
        
        # In a real implementation, this would connect to Twitter API
        await asyncio.sleep(0.1)  # Simulate API call
        
        result = {
            "success": True,
            "recipient_username": request.recipient_username,
            "message_sent": request.text,
            "timestamp": asyncio.get_event_loop().time(),
            "message_id": f"tw_dm_{hash(request.recipient_username + request.text) % 10000:04d}"
        }
        
        logger.info(f"Twitter DM sent successfully: {result['message_id']}")
        return result

    async def like_tweet(self, request) -> Dict[str, Any]:
        """
        Like a Twitter post.
        
        Args:
            request: Contains tweet ID to like
            
        Returns:
            Dict with success status
        """
        logger.info(f"Liking tweet {request.tweet_id}")
        
        # In a real implementation, this would connect to Twitter API
        await asyncio.sleep(0.05)  # Simulate API call
        
        result = {
            "success": True,
            "tweet_id": request.tweet_id,
            "timestamp": asyncio.get_event_loop().time(),
            "action": "liked"
        }
        
        logger.info(f"Tweet liked successfully: {request.tweet_id}")
        return result

    async def get_twitter_followers(self) -> Dict[str, Any]:
        """
        Retrieve Twitter followers.
        
        Returns:
            Dict with list of followers
        """
        logger.info("Retrieving Twitter followers")
        
        # In a real implementation, this would fetch followers from the API
        await asyncio.sleep(0.1)  # Simulate API call
        
        followers = [
            {"username": "follower1", "display_name": "Follower One", "id": "123456"},
            {"username": "follower2", "display_name": "Follower Two", "id": "789012"},
            {"username": "follower3", "display_name": "Follower Three", "id": "345678"}
        ]
        
        result = {
            "success": True,
            "followers": followers,
            "total_count": len(followers)
        }
        
        logger.info(f"Retrieved {len(followers)} Twitter followers")
        return result

    async def run(self):
        """Run the Twitter MCP server"""
        from mcp.server.stdio import stdio_server
        async with stdio_server(self.server) as make_session:
            async for session in make_session():
                # Keep the server running
                await session.until_closed()


class TwitterPostRequest(BaseModel):
    """Request to create a Twitter post (tweet)."""
    text: str = Field(..., description="Content of the tweet (max 280 characters)")
    media_url: str = Field(default="", description="Optional URL to media to attach to the tweet")


class TwitterThreadRequest(BaseModel):
    """Request to create a Twitter thread (series of tweets)."""
    tweets: List[str] = Field(..., description="List of tweet texts in the thread")


class TwitterReplyRequest(BaseModel):
    """Request to reply to a Twitter post."""
    tweet_id: str = Field(..., description="ID of the tweet to reply to")
    text: str = Field(..., description="Content of the reply")


class TwitterMessageRequest(BaseModel):
    """Request to send a Twitter direct message."""
    recipient_username: str = Field(..., description="Username of the recipient")
    text: str = Field(..., description="Message content to send")


class TwitterLikeRequest(BaseModel):
    """Request to like a Twitter post."""
    tweet_id: str = Field(..., description="ID of the tweet to like")


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Entry point for running the server
async def serve():
    """Run the Twitter MCP server."""
    server = TwitterMCP()
    await server.run()


if __name__ == "__main__":
    asyncio.run(serve())