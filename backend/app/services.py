import json
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path
import re
from dateutil import parser as date_parser
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv

from .models import Event, EventCreate, EventUpdate, EventParseRequest

# LLM imports
import openai
from fastapi import HTTPException, status

# Google Calendar integration
from .google_calendar import google_calendar_service
from .mcp_client import mcp_client

# Load environment variables from project root
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / ".env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

class EventService:
    def __init__(self, data_file: str = "data/events.json"):
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_data_file_exists()

    def _ensure_data_file_exists(self):
        """Ensure the data file exists with an empty events array"""
        if not self.data_file.exists():
            self.data_file.write_text('{"events": []}')

    def _load_events(self) -> List[Dict[str, Any]]:
        """Load events from JSON file (fallback)"""
        try:
            data = json.loads(self.data_file.read_text())
            return data.get("events", [])
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_events(self, events: List[Dict[str, Any]]):
        """Save events to JSON file (fallback)"""
        print(f"DEBUG: Writing to file path: {os.path.abspath(self.data_file)}")
        print(f"DEBUG: Current working directory: {os.getcwd()}")
        data = {"events": events}
        self.data_file.write_text(json.dumps(data, indent=2, default=str))

    def _google_calendar_available(self) -> bool:
        """Check if Google Calendar is available and authenticated"""
        try:
            # Try MCP client first, fallback to direct API
            return mcp_client.initialized or google_calendar_service.service is not None
        except:
            return False

    def _convert_google_event_to_event(self, google_event: Dict[str, Any]) -> Event:
        """Convert Google Calendar event format to our Event model"""
        try:
            # Parse datetime strings
            start_time = date_parser.parse(google_event['start_time'])
            end_time = date_parser.parse(google_event['end_time'])
            
            # Create Event object
            event_data = {
                'id': google_event['id'],
                'title': google_event['title'],
                'description': google_event.get('description'),
                'start_time': start_time,
                'end_time': end_time,
                'location': google_event.get('location'),
                'priority': 'medium',  # Default for Google Calendar events
                'status': 'confirmed',  # Default for Google Calendar events
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'google_calendar_id': google_event['google_calendar_id']
            }
            
            return Event(**event_data)
        except Exception as e:
            print(f"Error converting Google event: {e}")
            raise

    def _convert_mcp_event_to_event(self, mcp_event: Dict[str, Any]) -> Event:
        """Convert MCP event format to our Event model"""
        try:
            # MCP events have different structure
            start_time = date_parser.parse(mcp_event['start']['dateTime'] if 'dateTime' in mcp_event['start'] else mcp_event['start']['date'])
            end_time = date_parser.parse(mcp_event['end']['dateTime'] if 'dateTime' in mcp_event['end'] else mcp_event['end']['date'])
            
            # Create Event object
            event_data = {
                'id': mcp_event['id'],
                'title': mcp_event['summary'],
                'description': mcp_event.get('description'),
                'start_time': start_time,
                'end_time': end_time,
                'location': mcp_event.get('location'),
                'priority': 'medium',  # Default for Google Calendar events
                'status': 'confirmed',  # Default for Google Calendar events
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'google_calendar_id': mcp_event['id']
            }
            
            return Event(**event_data)
        except Exception as e:
            print(f"Error converting MCP event: {e}")
            raise

    async def get_all_events(self) -> List[Event]:
        """Get all events - try MCP client first, then direct API, fallback to JSON"""
        events = []
        
        # Try MCP client first
        if mcp_client.initialized:
            try:
                print("DEBUG: Fetching events via MCP client")
                mcp_events = await mcp_client.list_events()
                
                for mcp_event in mcp_events:
                    try:
                        # Since MCP client returns the same format as Google Calendar service,
                        # use the Google Calendar conversion method
                        event = self._convert_google_event_to_event(mcp_event)
                        events.append(event)
                    except Exception as e:
                        print(f"DEBUG: Error converting MCP event {mcp_event.get('title', 'Unknown')}: {e}")
                        continue
                
                print(f"DEBUG: Loaded {len(events)} events via MCP client")
                return events
                
            except Exception as e:
                print(f"DEBUG: MCP client failed, trying direct API: {e}")
        
        # Try direct Google Calendar API
        if self._google_calendar_available():
            try:
                print("DEBUG: Fetching events from Google Calendar (direct API)")
                google_events = google_calendar_service.get_events()
                
                for google_event in google_events:
                    try:
                        event = self._convert_google_event_to_event(google_event)
                        events.append(event)
                    except Exception as e:
                        print(f"DEBUG: Error converting Google event {google_event.get('title', 'Unknown')}: {e}")
                        continue
                
                print(f"DEBUG: Loaded {len(events)} events from Google Calendar")
                return events
                
            except Exception as e:
                print(f"DEBUG: Google Calendar failed, falling back to JSON: {e}")
        
        # Fallback to JSON
        print("DEBUG: Using JSON fallback for events")
        events_data = self._load_events()
        print(f"DEBUG: Raw events data: {events_data}")
        
        for event_data in events_data:
            try:
                event = Event(**event_data)
                events.append(event)
            except Exception as e:
                print(f"DEBUG: Skipping corrupted event {event_data}: {e}")
                continue
        
        return events

    async def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """Get event by ID - try MCP client first, then direct API, then JSON"""
        # Try MCP client first
        if mcp_client.initialized:
            try:
                # Note: This would need a specific MCP API call
                # For now, get all events and filter
                all_events = await self.get_all_events()
                for event in all_events:
                    if event.id == event_id:
                        return event
            except Exception as e:
                print(f"DEBUG: MCP client lookup failed: {e}")
        
        # Try direct Google Calendar API
        if self._google_calendar_available():
            try:
                # Note: This would need a specific Google Calendar API call
                # For now, get all events and filter
                all_events = await self.get_all_events()
                for event in all_events:
                    if event.id == event_id:
                        return event
            except Exception as e:
                print(f"DEBUG: Google Calendar lookup failed: {e}")
        
        # Fallback to JSON
        events_data = self._load_events()
        for event_data in events_data:
            if event_data.get("id") == event_id:
                return Event(**event_data)
        return None

    async def create_event(self, event: EventCreate) -> Event:
        """Create a new event - try MCP client first, then direct API, fallback to JSON"""
        print("DEBUG: EventCreate dict:", event.dict())
        new_event = Event(**event.dict())
        print("DEBUG: Event model created:", new_event)
        
        # Check for conflicts
        conflicts = await self.detect_conflicts(new_event)
        if conflicts:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"message": "Event time conflicts with existing event(s)", "conflicts": conflicts}
            )
        
        # Try MCP client first
        if mcp_client.initialized:
            try:
                print("DEBUG: Creating event via MCP client")
                mcp_event_data = {
                    'summary': event.title,
                    'description': event.description,
                    'start': {
                        'dateTime': event.start_time.isoformat(),
                        'timeZone': 'UTC'
                    },
                    'end': {
                        'dateTime': event.end_time.isoformat(),
                        'timeZone': 'UTC'
                    }
                }
                if event.location:
                    mcp_event_data['location'] = event.location
                
                mcp_event = await mcp_client.create_event(mcp_event_data)
                if mcp_event:
                    # Update our event with Google Calendar ID
                    new_event.id = mcp_event['id']
                    new_event.google_calendar_id = mcp_event['id']
                    print(f"DEBUG: Created event via MCP client: {new_event.title}")
                    return new_event
            except Exception as e:
                print(f"DEBUG: MCP client creation failed, trying direct API: {e}")
        
        # Try direct Google Calendar API
        if self._google_calendar_available():
            try:
                print("DEBUG: Creating event in Google Calendar (direct API)")
                google_event = google_calendar_service.create_event(event)
                if google_event:
                    # Update our event with Google Calendar ID
                    new_event.id = google_event['id']
                    new_event.google_calendar_id = google_event['google_calendar_id']
                    print(f"DEBUG: Created event in Google Calendar: {new_event.title}")
                    return new_event
            except Exception as e:
                print(f"DEBUG: Google Calendar creation failed, falling back to JSON: {e}")
        
        # Fallback to JSON
        print("DEBUG: Creating event in JSON storage")
        events_data = self._load_events()
        events_data.append(new_event.dict())
        self._save_events(events_data)
        return new_event

    def update_event(self, event_id: str, event_update: EventUpdate) -> Optional[Event]:
        """Update an existing event - try Google Calendar first, fallback to JSON"""
        # Try Google Calendar first
        if self._google_calendar_available():
            try:
                # Note: This would need specific Google Calendar API update call
                # For now, fallback to JSON
                pass
            except Exception as e:
                print(f"DEBUG: Google Calendar update failed: {e}")
        
        # Fallback to JSON
        events_data = self._load_events()
        for i, event_data in enumerate(events_data):
            if event_data.get("id") == event_id:
                # Update only provided fields
                update_data = event_update.dict(exclude_unset=True)
                update_data["updated_at"] = datetime.utcnow()
                events_data[i].update(update_data)
                self._save_events(events_data)
                return Event(**events_data[i])
        return None

    async def delete_event(self, event_id: str) -> bool:
        """Delete an event - try MCP client first, then direct API, fallback to JSON"""
        # Try MCP client first
        if mcp_client.initialized:
            try:
                # Check if this is a Google Calendar event
                event = await self.get_event_by_id(event_id)
                if event and hasattr(event, 'google_calendar_id') and event.google_calendar_id:
                    success = await mcp_client.delete_event("primary", event.google_calendar_id)
                    if success:
                        print(f"DEBUG: Deleted event via MCP client: {event.title}")
                        return True
            except Exception as e:
                print(f"DEBUG: MCP client deletion failed, trying direct API: {e}")
        
        # Try direct Google Calendar API
        if self._google_calendar_available():
            try:
                # Check if this is a Google Calendar event
                event = await self.get_event_by_id(event_id)
                if event and hasattr(event, 'google_calendar_id') and event.google_calendar_id:
                    success = google_calendar_service.delete_event(event.google_calendar_id)
                    if success:
                        print(f"DEBUG: Deleted event from Google Calendar: {event.title}")
                        return True
            except Exception as e:
                print(f"DEBUG: Google Calendar deletion failed: {e}")
        
        # Fallback to JSON
        events_data = self._load_events()
        for i, event_data in enumerate(events_data):
            if event_data.get("id") == event_id:
                events_data.pop(i)
                self._save_events(events_data)
                return True
        return False

    async def detect_conflicts(self, new_event: Event, exclude_event_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Detect scheduling conflicts with existing events"""
        print("DEBUG: Starting detect_conflicts")
        conflicts = []
        try:
            existing_events = await self.get_all_events()
            print(f"DEBUG: Loaded {len(existing_events)} existing events")
            for existing_event in existing_events:
                if exclude_event_id and existing_event.id == exclude_event_id:
                    continue
                # Check for time overlap
                if (
                    new_event.start_time < existing_event.end_time and
                    new_event.end_time > existing_event.start_time
                ):
                    conflicts.append({
                        "conflicting_event": existing_event.dict(),
                        "conflict_type": "time_overlap",
                        "message": f"Conflicts with '{existing_event.title}'"
                    })
        except Exception as e:
            print(f"DEBUG: Error in detect_conflicts: {e}")
            raise
        return conflicts

    async def check_conflicts(self, event: EventCreate) -> List[Dict[str, Any]]:
        """Check for conflicts without creating event"""
        new_event = Event(**event.dict())
        return await self.detect_conflicts(new_event)

    def get_storage_status(self) -> Dict[str, Any]:
        """Get the current storage status (Google Calendar vs JSON)"""
        google_available = self._google_calendar_available()
        return {
            "primary_storage": "google_calendar" if google_available else "json",
            "google_calendar_available": google_available,
            "fallback_available": True
        }

    def parse_event_text(self, text: str) -> List[Event]:
        """Parse unstructured event text into structured events using OpenAI LLM"""
        print(f"DEBUG: OPENAI_API_KEY present: {bool(OPENAI_API_KEY)}")
        if not OPENAI_API_KEY:
            print("DEBUG: No OpenAI API key found, returning empty list")
            return []
        
        try:
            today_str = datetime.now().strftime('%Y-%m-%d')
            prompt = f"""
Assume today is {today_str}.
Extract event details from this text and return a JSON array with exactly one event object.
Format: [{{"title": "event name", "start_time": "YYYY-MM-DDTHH:MM:SS", "end_time": "YYYY-MM-DDTHH:MM:SS", "location": "location if present"}}]
- If end_time is not specified, set it to exactly 1 hour after start_time.
- Ensure end_time is always after start_time.
- Return only valid JSON, no other text.

Text: {text}
"""
            print(f"DEBUG: Sending prompt to OpenAI: {prompt[:100]}...")
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=512,
            )
            content = response.choices[0].message.content.strip()
            print(f"DEBUG: OpenAI response: {content}")
            
            # Try to extract JSON from the response
            try:
                events_data = json.loads(content)
                print(f"DEBUG: Parsed JSON: {events_data}")
                
                # Validate and convert to Event objects
                events = []
                for event_dict in events_data:
                    # Parse datetimes
                    event_dict["start_time"] = date_parser.parse(event_dict["start_time"])
                    event_dict["end_time"] = date_parser.parse(event_dict["end_time"])
                    # Auto-correct end_time if needed
                    if event_dict["end_time"] <= event_dict["start_time"]:
                        event_dict["end_time"] = event_dict["start_time"] + timedelta(hours=1)
                    events.append(Event(**event_dict))
                print(f"DEBUG: Created {len(events)} events")
                return events
            except Exception as e:
                print(f"DEBUG: JSON parsing error: {e}")
                return []
        except Exception as e:
            print(f"DEBUG: OpenAI API error: {e}")
            return []

    def _parse_datetime(self, date_str: str, time_str: str) -> Optional[datetime]:
        """Parse date and time strings into datetime object"""
        try:
            # Handle different date formats
            if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                # ISO format
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            elif re.match(r'\d{1,2}/\d{1,2}', date_str):
                # MM/DD format - assume current year
                date_obj = datetime.strptime(f"{date_str}/{datetime.now().year}", '%m/%d/%Y')
            else:
                # Try to parse as day name or relative date
                date_obj = self._parse_relative_date(date_str)
            
            if not date_obj:
                return None
            
            # Parse time
            time_obj = self._parse_time(time_str)
            if not time_obj:
                return None
            
            # Combine date and time
            return datetime.combine(date_obj.date(), time_obj)
            
        except Exception:
            return None

    def _parse_relative_date(self, date_str: str) -> Optional[datetime]:
        """Parse relative dates like 'Monday', 'tomorrow', etc."""
        today = datetime.now()
        date_str_lower = date_str.lower()
        
        # Day names
        days = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        if date_str_lower in days:
            target_day = days[date_str_lower]
            current_day = today.weekday()
            days_ahead = target_day - current_day
            if days_ahead <= 0:  # Target day has passed this week
                days_ahead += 7
            return today + timedelta(days=days_ahead)
        
        # Relative dates
        if date_str_lower == 'today':
            return today
        elif date_str_lower == 'tomorrow':
            return today + timedelta(days=1)
        elif date_str_lower == 'next week':
            return today + timedelta(weeks=1)
        
        return None

    def _parse_time(self, time_str: str) -> Optional[datetime.time]:
        """Parse time string into time object"""
        try:
            # Remove AM/PM and normalize
            time_str_clean = re.sub(r'\s*(am|pm|AM|PM)\s*', '', time_str).strip()
            
            if ':' in time_str_clean:
                # HH:MM format
                hour, minute = map(int, time_str_clean.split(':'))
            else:
                # HH format
                hour = int(time_str_clean)
                minute = 0
            
            # Handle AM/PM
            if re.search(r'pm|PM', time_str) and hour != 12:
                hour += 12
            elif re.search(r'am|AM', time_str) and hour == 12:
                hour = 0
            
            return datetime.time(hour, minute)
        except Exception:
            return None


# Global service instance
event_service = EventService() 