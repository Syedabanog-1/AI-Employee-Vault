#!/usr/bin/env python3
"""
Twitter/X MCP Server
Provides tools for interacting with Twitter API v2 via Tweepy
through the Model Context Protocol.
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Dict, Any, List

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
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', '')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET', '')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN', '')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET', '')
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN', '')
DRY_RUN = os.getenv('DRY_RUN', 'false').lower() == 'true'


def _get_tweepy_client():
    """Build and return authenticated Tweepy Client (API v2)."""
    try:
        import tweepy
        client = tweepy.Client(
            bearer_token=TWITTER_BEARER_TOKEN,
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
            wait_on_rate_limit=True
        )
        return client
    except ImportError:
        logger.error("tweepy not installed — run: pip install tweepy")
        return None
    except Exception as e:
        logger.error(f"Failed to create Tweepy client: {e}")
        return None


class TwitterMCP:
    def __init__(self):
        self.server = Server("twitter-mcp")
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP capability handlers"""

        create_twitter_post_tool = Tool(
            name="create_twitter_post",
            description="Create a tweet on the authenticated Twitter/X account",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Content of the tweet (max 280 characters)"
                    }
                },
                "required": ["text"]
            }
        )

        create_twitter_thread_tool = Tool(
            name="create_twitter_thread",
            description="Create a thread of tweets on the authenticated Twitter/X account",
            inputSchema={
                "type": "object",
                "properties": {
                    "tweets": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of tweet texts in the thread (each max 280 chars)"
                    }
                },
                "required": ["tweets"]
            }
        )

        reply_to_tweet_tool = Tool(
            name="reply_to_tweet",
            description="Reply to an existing tweet",
            inputSchema={
                "type": "object",
                "properties": {
                    "tweet_id": {
                        "type": "string",
                        "description": "ID of the tweet to reply to"
                    },
                    "text": {
                        "type": "string",
                        "description": "Content of the reply (max 280 characters)"
                    }
                },
                "required": ["tweet_id", "text"]
            }
        )

        like_tweet_tool = Tool(
            name="like_tweet",
            description="Like an existing tweet",
            inputSchema={
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

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                create_twitter_post_tool,
                create_twitter_thread_tool,
                reply_to_tweet_tool,
                like_tweet_tool,
            ]

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
            elif name == "like_tweet":
                request = TwitterLikeRequest(**arguments)
                return [await self.like_tweet(request)]
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def create_twitter_post(self, request) -> Dict[str, Any]:
        """Create a tweet using Twitter API v2."""
        logger.info(f"Creating tweet: {request.text[:60]}...")

        if DRY_RUN:
            logger.info(f"[DRY RUN] Would tweet: '{request.text}'")
            return {
                "success": True,
                "dry_run": True,
                "text": request.text,
                "timestamp": datetime.now().isoformat()
            }

        if not TWITTER_API_KEY:
            return {"success": False, "error": "Twitter API credentials not configured"}

        client = _get_tweepy_client()
        if not client:
            return {"success": False, "error": "Failed to initialize Tweepy client"}

        try:
            response = client.create_tweet(text=request.text)
            tweet_id = response.data['id']
            logger.info(f"Tweet created: {tweet_id}")
            return {
                "success": True,
                "tweet_id": tweet_id,
                "text": request.text,
                "url": f"https://twitter.com/i/web/status/{tweet_id}",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error creating tweet: {e}")
            return {"success": False, "error": str(e)}

    async def create_twitter_thread(self, request) -> Dict[str, Any]:
        """Create a Twitter thread by posting tweets as replies to each other."""
        logger.info(f"Creating Twitter thread with {len(request.tweets)} tweets")

        if DRY_RUN:
            return {
                "success": True,
                "dry_run": True,
                "tweet_count": len(request.tweets),
                "timestamp": datetime.now().isoformat()
            }

        if not TWITTER_API_KEY:
            return {"success": False, "error": "Twitter API credentials not configured"}

        client = _get_tweepy_client()
        if not client:
            return {"success": False, "error": "Failed to initialize Tweepy client"}

        tweet_ids = []
        last_tweet_id = None

        try:
            for tweet_text in request.tweets:
                kwargs = {"text": tweet_text}
                if last_tweet_id:
                    kwargs["reply"] = {"in_reply_to_tweet_id": last_tweet_id}

                response = client.create_tweet(**kwargs)
                last_tweet_id = response.data['id']
                tweet_ids.append(last_tweet_id)
                logger.info(f"Thread tweet created: {last_tweet_id}")

            return {
                "success": True,
                "tweet_ids": tweet_ids,
                "tweet_count": len(tweet_ids),
                "thread_url": f"https://twitter.com/i/web/status/{tweet_ids[0]}" if tweet_ids else "",
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error creating thread: {e}")
            return {"success": False, "error": str(e), "tweets_posted": len(tweet_ids)}

    async def reply_to_tweet(self, request) -> Dict[str, Any]:
        """Reply to an existing tweet."""
        logger.info(f"Replying to tweet {request.tweet_id}")

        if DRY_RUN:
            return {"success": True, "dry_run": True, "in_reply_to": request.tweet_id}

        if not TWITTER_API_KEY:
            return {"success": False, "error": "Twitter API credentials not configured"}

        client = _get_tweepy_client()
        if not client:
            return {"success": False, "error": "Failed to initialize Tweepy client"}

        try:
            response = client.create_tweet(
                text=request.text,
                reply={"in_reply_to_tweet_id": request.tweet_id}
            )
            reply_id = response.data['id']
            return {
                "success": True,
                "reply_id": reply_id,
                "in_reply_to": request.tweet_id,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error replying to tweet: {e}")
            return {"success": False, "error": str(e)}

    async def like_tweet(self, request) -> Dict[str, Any]:
        """Like a tweet."""
        logger.info(f"Liking tweet {request.tweet_id}")

        if DRY_RUN:
            return {"success": True, "dry_run": True, "tweet_id": request.tweet_id}

        if not TWITTER_API_KEY:
            return {"success": False, "error": "Twitter API credentials not configured"}

        client = _get_tweepy_client()
        if not client:
            return {"success": False, "error": "Failed to initialize Tweepy client"}

        try:
            # Get authenticated user ID first
            me = client.get_me()
            user_id = me.data.id
            client.like(user_id, request.tweet_id)
            return {
                "success": True,
                "tweet_id": request.tweet_id,
                "action": "liked",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error liking tweet: {e}")
            return {"success": False, "error": str(e)}

    async def run(self):
        """Run the Twitter MCP server via stdio."""
        from mcp.server.stdio import stdio_server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


# --- Pydantic request models ---

class TwitterPostRequest(BaseModel):
    text: str = Field(..., description="Content of the tweet (max 280 characters)")


class TwitterThreadRequest(BaseModel):
    tweets: List[str] = Field(..., description="List of tweet texts in the thread")


class TwitterReplyRequest(BaseModel):
    tweet_id: str = Field(..., description="ID of the tweet to reply to")
    text: str = Field(..., description="Content of the reply")


class TwitterLikeRequest(BaseModel):
    tweet_id: str = Field(..., description="ID of the tweet to like")


async def serve():
    """Entry point for running the Twitter MCP server."""
    server = TwitterMCP()
    await server.run()


if __name__ == "__main__":
    asyncio.run(serve())
