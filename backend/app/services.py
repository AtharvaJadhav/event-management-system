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
        """Load events from JSON file"""
        try:
            data = json.loads(self.data_file.read_text())
            return data.get("events", [])
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _save_events(self, events: List[Dict[str, Any]]):
        """Save events to JSON file"""
        print(f"DEBUG: Writing to file path: {os.path.abspath(self.data_file)}")
        print(f"DEBUG: Current working directory: {os.getcwd()}")
        data = {"events": events}
        self.data_file.write_text(json.dumps(data, indent=2, default=str))

    def get_all_events(self) -> List[Event]:
        """Get all events"""
        events_data = self._load_events()
        print(f"DEBUG: Raw events data: {events_data}")
        events = []
        for event_data in events_data:
            try:
                event = Event(**event_data)
                events.append(event)
            except Exception as e:
                print(f"DEBUG: Skipping corrupted event {event_data}: {e}")
                # Skip corrupted events instead of failing
                continue
        return events

    def get_event_by_id(self, event_id: str) -> Optional[Event]:
        """Get event by ID"""
        events_data = self._load_events()
        for event_data in events_data:
            if event_data.get("id") == event_id:
                return Event(**event_data)
        return None

    def create_event(self, event: EventCreate) -> Event:
        """Create a new event, prevent conflicts"""
        print("DEBUG: EventCreate dict:", event.dict())
        new_event = Event(**event.dict())
        print("DEBUG: Event model created:", new_event)
        # conflicts = self.detect_conflicts(new_event)
        # if conflicts:
        #     raise HTTPException(
        #         status_code=status.HTTP_409_CONFLICT,
        #         detail={"message": "Event time conflicts with existing event(s)", "conflicts": conflicts}
        #     )
        events_data = self._load_events()
        events_data.append(new_event.dict())
        self._save_events(events_data)
        return new_event

    def update_event(self, event_id: str, event_update: EventUpdate) -> Optional[Event]:
        """Update an existing event"""
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

    def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
        events_data = self._load_events()
        for i, event_data in enumerate(events_data):
            if event_data.get("id") == event_id:
                events_data.pop(i)
                self._save_events(events_data)
                return True
        return False

    def detect_conflicts(self, new_event: Event, exclude_event_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Detect scheduling conflicts with existing events"""
        print("DEBUG: Starting detect_conflicts")
        conflicts = []
        try:
            existing_events = self.get_all_events()
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

    def check_conflicts(self, event: EventCreate) -> List[Dict[str, Any]]:
        """Check for conflicts without creating event"""
        new_event = Event(**event.dict())
        return self.detect_conflicts(new_event)

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