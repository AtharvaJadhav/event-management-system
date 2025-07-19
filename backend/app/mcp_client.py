import asyncio
import json
import subprocess
import sys
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta

class GoogleCalendarMCPClient:
    """MCP client wrapper for Google Calendar operations"""
    
    def __init__(self, credentials_path: str = "backend/gcp-oauth.keys.json"):
        self.credentials_path = Path(credentials_path)
        self.initialized = True  # Mark as initialized for fallback testing
        
    async def _run_mcp_command(self, command: str, args: List[str] = None) -> Dict[str, Any]:
        """Run MCP command using npx"""
        try:
            env = os.environ.copy()
            env['GOOGLE_OAUTH_CREDENTIALS'] = str(self.credentials_path.absolute())
            
            cmd = [sys.executable, '-m', 'npx', '@cocal/google-calendar-mcp', command]
            if args:
                cmd.extend(args)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=30
            )
            
            if result.returncode != 0:
                raise Exception(f"MCP command failed: {result.stderr}")
                
            return {"success": True, "output": result.stdout}
            
        except Exception as e:
            print(f"MCP command failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call MCP tool using the server"""
        try:
            # For now, we'll use a simpler approach - direct API calls
            # In a full implementation, you'd use the MCP protocol
            print(f"Calling MCP tool: {tool_name} with args: {arguments}")
            return {"success": True, "content": []}
            
        except Exception as e:
            print(f"MCP tool call failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def list_calendars(self) -> List[Dict[str, Any]]:
        """List available calendars"""
        try:
            # For now, return a simple primary calendar
            return [{"id": "primary", "summary": "Primary Calendar"}]
        except Exception as e:
            print(f"Failed to list calendars: {e}")
            return []
    
    async def list_events(self, calendar_id: str = "primary", max_results: int = 50) -> List[Dict[str, Any]]:
        """List events from a calendar"""
        try:
            # Use the existing Google Calendar service as fallback
            from .google_calendar import google_calendar_service
            events = google_calendar_service.get_events(max_results=max_results)
            return events
        except Exception as e:
            print(f"Failed to list events: {e}")
            return []
    
    async def create_event(self, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new event"""
        try:
            # Use the existing Google Calendar service as fallback
            from .google_calendar import google_calendar_service
            from .models import EventCreate
            from datetime import datetime
            
            # Convert MCP event data to EventCreate
            event_create = EventCreate(
                title=event_data['summary'],
                description=event_data.get('description'),
                start_time=datetime.fromisoformat(event_data['start']['dateTime'].replace('Z', '+00:00')),
                end_time=datetime.fromisoformat(event_data['end']['dateTime'].replace('Z', '+00:00')),
                location=event_data.get('location')
            )
            
            result = google_calendar_service.create_event(event_create)
            return result
        except Exception as e:
            print(f"Failed to create event: {e}")
            return None
    
    async def delete_event(self, calendar_id: str, event_id: str) -> bool:
        """Delete an event"""
        try:
            # Use the existing Google Calendar service as fallback
            from .google_calendar import google_calendar_service
            result = google_calendar_service.delete_event(event_id)
            return result
        except Exception as e:
            print(f"Failed to delete event: {e}")
            return False
    
    async def search_events(self, query: str, calendar_id: str = "primary") -> List[Dict[str, Any]]:
        """Search events by text query"""
        try:
            # For now, return empty list - will be handled by fallback
            return []
        except Exception as e:
            print(f"Failed to search events: {e}")
            return []
    
    async def get_freebusy(self, time_min: str, time_max: str, calendar_ids: List[str] = None) -> Dict[str, Any]:
        """Get free/busy information"""
        try:
            # For now, return empty dict - will be handled by fallback
            return {}
        except Exception as e:
            print(f"Failed to get free/busy: {e}")
            return {}
    
    def stop(self):
        """Stop the MCP server"""
        self.initialized = False
        print("MCP client stopped")

# Global instance
mcp_client = GoogleCalendarMCPClient() 