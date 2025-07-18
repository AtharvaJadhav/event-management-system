#!/usr/bin/env python3
"""
Test script for Google Calendar integration.
Run this to verify the connection works before integrating with the main app.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent))

from app.google_calendar import GoogleCalendarService

def test_google_calendar():
    """Test Google Calendar integration."""
    print("🔍 Testing Google Calendar Integration...")
    
    # Initialize the service
    service = GoogleCalendarService()
    
    # Test authentication
    print("1. Testing authentication...")
    if service.authenticate():
        print("✅ Authentication successful!")
    else:
        print("❌ Authentication failed!")
        return False
    
    # Test reading events
    print("2. Testing event reading...")
    events = service.get_events(max_results=5)
    print(f"✅ Found {len(events)} events in Google Calendar")
    
    if events:
        print("Sample events:")
        for event in events[:3]:  # Show first 3 events
            print(f"  - {event['title']} ({event['start_time']})")
    
    # Test creating a test event
    print("3. Testing event creation...")
    from app.models import EventCreate
    from datetime import datetime, timedelta
    
    test_event = EventCreate(
        title="Test Event from API",
        description="This is a test event created by the API integration",
        start_time=datetime.now() + timedelta(hours=1),
        end_time=datetime.now() + timedelta(hours=2),
        location="Test Location"
    )
    
    created_event = service.create_event(test_event)
    if created_event:
        print(f"✅ Test event created: {created_event['title']}")
        
        # Test deleting the test event
        print("4. Testing event deletion...")
        if service.delete_event(created_event['id']):
            print("✅ Test event deleted successfully!")
        else:
            print("❌ Failed to delete test event!")
    else:
        print("❌ Failed to create test event!")
    
    print("\n🎉 Google Calendar integration test completed!")
    return True

if __name__ == "__main__":
    test_google_calendar() 