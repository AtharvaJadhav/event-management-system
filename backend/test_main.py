#!/usr/bin/env python3
"""
Simple test script for the Event Management System backend
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend. Is it running?")
        return False

def test_event_parsing():
    """Test event parsing functionality"""
    print("\n🔍 Testing event parsing...")
    
    test_texts = [
        "Chuck's soccer game moved to Thursday at 3:30pm",
        "Team meeting tomorrow at 2pm",
        "Doctor appointment on Friday at 10am"
    ]
    
    for text in test_texts:
        try:
            response = requests.post(
                f"{BASE_URL}/api/events/parse",
                json={"text": text}
            )
            if response.status_code == 200:
                data = response.json()
                events = data.get("events", [])
                conflicts = data.get("conflicts", [])
                print(f"✅ Parsed '{text}' -> {len(events)} events, {len(conflicts)} conflicts")
            else:
                print(f"❌ Failed to parse '{text}': {response.status_code}")
        except Exception as e:
            print(f"❌ Error parsing '{text}': {e}")

def test_event_crud():
    """Test CRUD operations for events"""
    print("\n🔍 Testing event CRUD operations...")
    
    # Create event
    event_data = {
        "title": "Test Event",
        "description": "A test event for API testing",
        "start_time": (datetime.now() + timedelta(hours=1)).isoformat(),
        "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
        "location": "Test Location",
        "priority": "medium"
    }
    
    try:
        # Create
        response = requests.post(f"{BASE_URL}/api/events", json=event_data)
        if response.status_code == 201:
            created_event = response.json()
            event_id = created_event["id"]
            print(f"✅ Created event: {created_event['title']}")
            
            # Read
            response = requests.get(f"{BASE_URL}/api/events/{event_id}")
            if response.status_code == 200:
                print("✅ Retrieved event")
                
                # Update
                update_data = {"title": "Updated Test Event"}
                response = requests.put(f"{BASE_URL}/api/events/{event_id}", json=update_data)
                if response.status_code == 200:
                    print("✅ Updated event")
                    
                    # Delete
                    response = requests.delete(f"{BASE_URL}/api/events/{event_id}")
                    if response.status_code == 204:
                        print("✅ Deleted event")
                    else:
                        print(f"❌ Failed to delete event: {response.status_code}")
                else:
                    print(f"❌ Failed to update event: {response.status_code}")
            else:
                print(f"❌ Failed to retrieve event: {response.status_code}")
        else:
            print(f"❌ Failed to create event: {response.status_code}")
    except Exception as e:
        print(f"❌ Error in CRUD test: {e}")

def main():
    """Run all tests"""
    print("🧪 Running Event Management System Backend Tests")
    print("=" * 50)
    
    if not test_health():
        print("\n❌ Backend is not running. Please start it first.")
        return
    
    test_event_parsing()
    test_event_crud()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")

if __name__ == "__main__":
    main() 