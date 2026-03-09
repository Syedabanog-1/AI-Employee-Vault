"""
Google Calendar MCP Server for AI Employee
Provides real Google Calendar operations through Model Context Protocol.
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
from pathlib import Path

from pydantic import BaseModel, Field
from mcp.server import Server
from mcp.types import Tool

# Load .env from vault root
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent.parent / '.env')
except ImportError:
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("calendar-mcp")

# Config
TOKEN_PATH = Path(os.getenv('GOOGLE_CALENDAR_TOKEN_PATH', './credentials/calendar_token.json'))
CLIENT_SECRET_PATH = Path(os.getenv('GOOGLE_CLIENT_SECRET_PATH', './credentials/client_secret.json'))
DRY_RUN = os.getenv('DRY_RUN', 'false').lower() == 'true'
SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_calendar_service():
    """Build and return an authenticated Google Calendar service."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = None

    # Resolve token path relative to vault root if not absolute
    token_path = TOKEN_PATH if TOKEN_PATH.is_absolute() else (
        Path(__file__).parent.parent.parent / TOKEN_PATH
    )

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, 'w') as f:
                f.write(creds.to_json())
        else:
            raise RuntimeError(
                f"Calendar token not found or invalid at {token_path}. "
                "Run: python credentials/calendar_auth_setup.py"
            )

    return build('calendar', 'v3', credentials=creds)


class CalendarMCP:
    def __init__(self):
        self.server = Server("calendar-mcp")
        self._setup_handlers()

    def _setup_handlers(self):
        create_event_tool = Tool(
            name="create_event",
            description="Create a new event in Google Calendar",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Title/summary of the event"},
                    "description": {"type": "string", "description": "Event description or notes"},
                    "start_time": {
                        "type": "string",
                        "description": "Start time in ISO 8601 format (e.g. 2026-02-25T10:00:00)"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End time in ISO 8601 format (e.g. 2026-02-25T11:00:00)"
                    },
                    "attendees": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of attendee email addresses"
                    },
                    "location": {"type": "string", "description": "Physical or virtual location"}
                },
                "required": ["title", "start_time", "end_time"]
            }
        )

        list_events_tool = Tool(
            name="list_events",
            description="List Google Calendar events within a date range",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of events to return (default: 20)"
                    }
                },
                "required": ["start_date", "end_date"]
            }
        )

        find_free_slots_tool = Tool(
            name="find_free_slots",
            description="Find free time slots in Google Calendar using freebusy query",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format"
                    },
                    "duration_minutes": {
                        "type": "integer",
                        "description": "Minimum duration of free slot in minutes"
                    }
                },
                "required": ["start_date", "end_date", "duration_minutes"]
            }
        )

        delete_event_tool = Tool(
            name="delete_event",
            description="Delete a Google Calendar event by its event ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "string",
                        "description": "The Google Calendar event ID to delete"
                    }
                },
                "required": ["event_id"]
            }
        )

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [create_event_tool, list_events_tool, find_free_slots_tool, delete_event_tool]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
            if name == "create_event":
                result = await self.create_event(
                    title=arguments["title"],
                    description=arguments.get("description", ""),
                    start_time=arguments["start_time"],
                    end_time=arguments["end_time"],
                    attendees=arguments.get("attendees", []),
                    location=arguments.get("location", "")
                )
            elif name == "list_events":
                result = await self.list_events(
                    start_date=arguments["start_date"],
                    end_date=arguments["end_date"],
                    max_results=arguments.get("max_results", 20)
                )
            elif name == "find_free_slots":
                result = await self.find_free_slots(
                    start_date=arguments["start_date"],
                    end_date=arguments["end_date"],
                    duration_minutes=arguments["duration_minutes"]
                )
            elif name == "delete_event":
                result = await self.delete_event(event_id=arguments["event_id"])
            else:
                raise ValueError(f"Unknown tool: {name}")
            return [result]

    async def create_event(self, title: str, description: str, start_time: str,
                           end_time: str, attendees: List[str], location: str) -> Dict[str, Any]:
        try:
            if DRY_RUN:
                logger.info(f"[DRY_RUN] Would create event: {title} from {start_time} to {end_time}")
                return {
                    "success": True,
                    "dry_run": True,
                    "event_id": "dry-run-id",
                    "title": title,
                    "start_time": start_time,
                    "end_time": end_time,
                    "html_link": "https://calendar.google.com"
                }

            service = get_calendar_service()

            event_body = {
                "summary": title,
                "description": description,
                "start": {"dateTime": start_time, "timeZone": "UTC"},
                "end": {"dateTime": end_time, "timeZone": "UTC"},
            }
            if attendees:
                event_body["attendees"] = [{"email": e} for e in attendees]
            if location:
                event_body["location"] = location

            event = service.events().insert(calendarId='primary', body=event_body).execute()

            logger.info(f"Event created: {event.get('htmlLink')}")
            return {
                "success": True,
                "event_id": event["id"],
                "title": event.get("summary"),
                "start_time": event["start"].get("dateTime"),
                "end_time": event["end"].get("dateTime"),
                "html_link": event.get("htmlLink")
            }
        except Exception as e:
            logger.error(f"create_event failed: {e}")
            return {"success": False, "error": str(e)}

    async def list_events(self, start_date: str, end_date: str,
                          max_results: int = 20) -> Dict[str, Any]:
        try:
            if DRY_RUN:
                logger.info(f"[DRY_RUN] Would list events from {start_date} to {end_date}")
                return {
                    "success": True,
                    "dry_run": True,
                    "events": [],
                    "count": 0
                }

            service = get_calendar_service()

            time_min = datetime.fromisoformat(start_date).replace(
                hour=0, minute=0, second=0, tzinfo=timezone.utc
            ).isoformat()
            time_max = datetime.fromisoformat(end_date).replace(
                hour=23, minute=59, second=59, tzinfo=timezone.utc
            ).isoformat()

            result = service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = []
            for item in result.get('items', []):
                start = item['start'].get('dateTime', item['start'].get('date'))
                end = item['end'].get('dateTime', item['end'].get('date'))
                events.append({
                    "id": item["id"],
                    "title": item.get("summary", "(no title)"),
                    "description": item.get("description", ""),
                    "start_time": start,
                    "end_time": end,
                    "location": item.get("location", ""),
                    "attendees": [a["email"] for a in item.get("attendees", [])],
                    "html_link": item.get("htmlLink")
                })

            return {"success": True, "events": events, "count": len(events)}
        except Exception as e:
            logger.error(f"list_events failed: {e}")
            return {"success": False, "error": str(e)}

    async def find_free_slots(self, start_date: str, end_date: str,
                              duration_minutes: int) -> Dict[str, Any]:
        try:
            if DRY_RUN:
                logger.info(f"[DRY_RUN] Would find free slots from {start_date} to {end_date}")
                return {
                    "success": True,
                    "dry_run": True,
                    "free_slots": [],
                    "count": 0
                }

            service = get_calendar_service()

            time_min = datetime.fromisoformat(start_date).replace(
                hour=0, minute=0, second=0, tzinfo=timezone.utc
            ).isoformat()
            time_max = datetime.fromisoformat(end_date).replace(
                hour=23, minute=59, second=59, tzinfo=timezone.utc
            ).isoformat()

            freebusy_result = service.freebusy().query(body={
                "timeMin": time_min,
                "timeMax": time_max,
                "items": [{"id": "primary"}]
            }).execute()

            busy_periods = freebusy_result["calendars"]["primary"].get("busy", [])

            # Compute free slots within business hours (9 AM – 5 PM UTC) each day
            free_slots = []
            current_date = datetime.fromisoformat(start_date).date()
            end_check_date = datetime.fromisoformat(end_date).date()
            duration = timedelta(minutes=duration_minutes)

            while current_date <= end_check_date:
                day_start = datetime(current_date.year, current_date.month, current_date.day,
                                     9, 0, 0, tzinfo=timezone.utc)
                day_end = datetime(current_date.year, current_date.month, current_date.day,
                                   17, 0, 0, tzinfo=timezone.utc)

                # Get busy times for this day
                day_busy = []
                for b in busy_periods:
                    b_start = datetime.fromisoformat(b["start"].replace("Z", "+00:00"))
                    b_end = datetime.fromisoformat(b["end"].replace("Z", "+00:00"))
                    if b_start.date() == current_date or b_end.date() == current_date:
                        day_busy.append((b_start, b_end))
                day_busy.sort(key=lambda x: x[0])

                # Walk through the day finding gaps
                cursor = day_start
                for b_start, b_end in day_busy:
                    if cursor + duration <= b_start:
                        free_slots.append({
                            "start_time": cursor.isoformat(),
                            "end_time": (cursor + duration).isoformat(),
                            "duration_minutes": duration_minutes
                        })
                    cursor = max(cursor, b_end)

                if cursor + duration <= day_end:
                    free_slots.append({
                        "start_time": cursor.isoformat(),
                        "end_time": (cursor + duration).isoformat(),
                        "duration_minutes": duration_minutes
                    })

                current_date += timedelta(days=1)

            return {"success": True, "free_slots": free_slots, "count": len(free_slots)}
        except Exception as e:
            logger.error(f"find_free_slots failed: {e}")
            return {"success": False, "error": str(e)}

    async def delete_event(self, event_id: str) -> Dict[str, Any]:
        try:
            if DRY_RUN:
                logger.info(f"[DRY_RUN] Would delete event: {event_id}")
                return {"success": True, "dry_run": True, "event_id": event_id}

            service = get_calendar_service()
            service.events().delete(calendarId='primary', eventId=event_id).execute()
            logger.info(f"Event deleted: {event_id}")
            return {"success": True, "event_id": event_id, "message": "Event deleted"}
        except Exception as e:
            logger.error(f"delete_event failed: {e}")
            return {"success": False, "error": str(e)}

    async def run(self):
        """Run the MCP server via stdio."""
        from mcp.server.stdio import stdio_server
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def serve():
    server = CalendarMCP()
    await server.run()


if __name__ == "__main__":
    asyncio.run(serve())
