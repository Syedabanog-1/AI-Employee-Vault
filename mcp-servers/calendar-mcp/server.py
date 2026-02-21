"""
Calendar MCP Server for AI Employee
Provides calendar operations through Model Context Protocol
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from mcp.server import Server
from mcp.types import Notification, Prompt, PromptResult, Tool
import uuid


class CalendarEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str = ""
    start_time: datetime
    end_time: datetime
    attendees: List[str] = Field(default_factory=list)
    location: str = ""


class CalendarMCP:
    def __init__(self):
        self.server = Server("calendar-mcp")
        self.events: List[CalendarEvent] = []
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP capability handlers"""
        
        # Define tools
        create_event_tool = Tool(
            name="create_event",
            description="Create a new calendar event",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Title of the event"},
                    "description": {"type": "string", "description": "Description of the event"},
                    "start_time": {"type": "string", "format": "date-time", "description": "Start time of the event (ISO format)"},
                    "end_time": {"type": "string", "format": "date-time", "description": "End time of the event (ISO format)"},
                    "attendees": {
                        "type": "array", 
                        "items": {"type": "string"}, 
                        "description": "List of attendee email addresses"
                    },
                    "location": {"type": "string", "description": "Location of the event"}
                },
                "required": ["title", "start_time", "end_time"]
            }
        )
        
        list_events_tool = Tool(
            name="list_events",
            description="List calendar events within a date range",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "format": "date", "description": "Start date (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "format": "date", "description": "End date (YYYY-MM-DD)"}
                },
                "required": ["start_date", "end_date"]
            }
        )
        
        find_free_slots_tool = Tool(
            name="find_free_slots",
            description="Find free time slots in the calendar",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "format": "date", "description": "Start date (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "format": "date", "description": "End date (YYYY-MM-DD)"},
                    "duration_minutes": {"type": "integer", "description": "Duration of the slot in minutes"}
                },
                "required": ["start_date", "end_date", "duration_minutes"]
            }
        )
        
        # Register tools
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                create_event_tool,
                list_events_tool,
                find_free_slots_tool
            ]

        # Register handlers
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
            if name == "create_event":
                return [await self.create_event(
                    arguments["title"],
                    arguments.get("description", ""),
                    arguments["start_time"],
                    arguments["end_time"],
                    arguments.get("attendees", []),
                    arguments.get("location", "")
                )]
            elif name == "list_events":
                return [await self.list_events(arguments["start_date"], arguments["end_date"])]
            elif name == "find_free_slots":
                return [await self.find_free_slots(
                    arguments["start_date"], 
                    arguments["end_date"], 
                    arguments["duration_minutes"]
                )]
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def create_event(self, title: str, description: str, start_time: str, end_time: str, 
                          attendees: List[str], location: str) -> Dict[str, Any]:
        """Create a new calendar event"""
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            event = CalendarEvent(
                title=title,
                description=description,
                start_time=start_dt,
                end_time=end_dt,
                attendees=attendees,
                location=location
            )
            
            self.events.append(event)
            
            return {
                "success": True,
                "event_id": event.id,
                "title": event.title,
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat()
            }
        except Exception as e:
            return {"error": f"Failed to create event: {str(e)}"}

    async def list_events(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """List calendar events within a date range"""
        try:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
            
            filtered_events = [
                event for event in self.events
                if start_dt.date() <= event.start_time.date() <= end_dt.date()
            ]
            
            events_list = []
            for event in filtered_events:
                events_list.append({
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "start_time": event.start_time.isoformat(),
                    "end_time": event.end_time.isoformat(),
                    "attendees": event.attendees,
                    "location": event.location
                })
            
            return {
                "success": True,
                "events": events_list,
                "count": len(events_list)
            }
        except Exception as e:
            return {"error": f"Failed to list events: {str(e)}"}

    async def find_free_slots(self, start_date: str, end_date: str, duration_minutes: int) -> Dict[str, Any]:
        """Find free time slots in the calendar"""
        try:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
            
            # For simplicity, we'll check each day individually
            current_date = start_dt.date()
            end_check_date = end_dt.date()
            
            free_slots = []
            
            while current_date <= end_check_date:
                # Define business hours (9 AM to 5 PM)
                day_start = datetime.combine(current_date, datetime.min.time().replace(hour=9))
                day_end = datetime.combine(current_date, datetime.min.time().replace(hour=17))
                
                # Get events for this day
                day_events = [
                    event for event in self.events
                    if event.start_time.date() == current_date
                ]
                
                # Sort events by start time
                day_events.sort(key=lambda x: x.start_time)
                
                # Check for free slots between events
                current_time = day_start
                for event in day_events:
                    if (event.start_time - current_time).total_seconds() >= duration_minutes * 60:
                        free_slots.append({
                            "start_time": current_time.isoformat(),
                            "end_time": (current_time + timedelta(minutes=duration_minutes)).isoformat(),
                            "duration_minutes": duration_minutes
                        })
                    
                    current_time = max(current_time, event.end_time)
                
                # Check for free slot after last event
                if (day_end - current_time).total_seconds() >= duration_minutes * 60:
                    free_slots.append({
                        "start_time": current_time.isoformat(),
                        "end_time": (current_time + timedelta(minutes=duration_minutes)).isoformat(),
                        "duration_minutes": duration_minutes
                    })
                
                current_date += timedelta(days=1)
            
            return {
                "success": True,
                "free_slots": free_slots,
                "count": len(free_slots)
            }
        except Exception as e:
            return {"error": f"Failed to find free slots: {str(e)}"}

    async def run(self):
        """Run the calendar MCP server"""
        from mcp.server.stdio import stdio_server
        async with stdio_server(self.server) as make_session:
            async for session in make_session():
                # Keep the server running
                await session.until_closed()


# Entry point
async def main():
    server = CalendarMCP()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())