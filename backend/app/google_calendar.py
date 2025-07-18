import os
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .models import Event, EventCreate

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarService:
    def __init__(self, credentials_file: str = "credentials.json"):
        self.credentials_file = Path(credentials_file)
        self.service = None
        self.creds = None

    def authenticate(self) -> bool:
        """Authenticate with Google Calendar API using OAuth2."""
        try:
            # The file token.json stores the user's access and refresh tokens.
            token_file = Path("token.json")
            
            if token_file.exists():
                self.creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
            
            # If there are no (valid) credentials available, let the user log in.
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not self.credentials_file.exists():
                        raise FileNotFoundError(f"Credentials file not found: {self.credentials_file}")
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_file), SCOPES,
                        redirect_uri='http://localhost:8000/auth/callback')
                    self.creds = flow.run_local_server(port=8000)
                
                # Save the credentials for the next run
                with open(token_file, 'w') as token:
                    token.write(self.creds.to_json())
            
            self.service = build('calendar', 'v3', credentials=self.creds)
            return True
            
        except Exception as e:
            print(f"Authentication error: {e}")
            return False

    def get_events(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """Fetch events from the primary calendar."""
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            # Call the Calendar API
            now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Convert to our format
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                formatted_events.append({
                    'id': event['id'],
                    'title': event['summary'],
                    'description': event.get('description'),
                    'start_time': start,
                    'end_time': end,
                    'location': event.get('location'),
                    'google_calendar_id': event['id']
                })
            
            return formatted_events
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []

    def create_event(self, event: EventCreate) -> Optional[Dict[str, Any]]:
        """Create a new event in Google Calendar."""
        if not self.service:
            if not self.authenticate():
                return None
        
        try:
            # Convert our event format to Google Calendar format
            google_event = {
                'summary': event.title,
                'description': event.description,
                'start': {
                    'dateTime': event.start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': event.end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }
            
            if event.location:
                google_event['location'] = event.location
            
            event_result = self.service.events().insert(
                calendarId='primary',
                body=google_event
            ).execute()
            
            return {
                'id': event_result['id'],
                'title': event_result['summary'],
                'description': event_result.get('description'),
                'start_time': event_result['start']['dateTime'],
                'end_time': event_result['end']['dateTime'],
                'location': event_result.get('location'),
                'google_calendar_id': event_result['id']
            }
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

    def delete_event(self, event_id: str) -> bool:
        """Delete an event from Google Calendar."""
        if not self.service:
            if not self.authenticate():
                return False
        
        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            return True
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            return False

    def sync_events(self) -> Dict[str, Any]:
        """Sync events from Google Calendar and return conflicts with local events."""
        google_events = self.get_events()
        
        # For now, return the Google events
        # In a full implementation, you'd compare with local events
        return {
            'google_events': google_events,
            'conflicts': [],  # TODO: Implement conflict detection
            'synced_count': len(google_events)
        }

# Global instance
google_calendar_service = GoogleCalendarService() 