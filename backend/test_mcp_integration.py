#!/usr/bin/env python3
"""
Test script for MCP client integration.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent))

async def test_mcp_integration():
    """Test MCP client integration."""
    print("🔍 Testing MCP Client Integration...")
    
    try:
        from app.mcp_client import mcp_client
        
        # Test MCP client initialization
        print("1. Testing MCP client initialization...")
        
        # Test listing calendars
        print("2. Testing calendar listing...")
        calendars = await mcp_client.list_calendars()
        print(f"✅ Found {len(calendars)} calendars")
        
        if calendars:
            print("Sample calendars:")
            for calendar in calendars[:3]:  # Show first 3 calendars
                print(f"  - {calendar.get('summary', 'Unknown')} ({calendar.get('id', 'No ID')})")
        
        # Test listing events
        print("3. Testing event listing...")
        events = await mcp_client.list_events(max_results=5)
        print(f"✅ Found {len(events)} events")
        
        if events:
            print("Sample events:")
            for event in events[:3]:  # Show first 3 events
                print(f"  - {event.get('summary', 'Unknown')} ({event.get('start', {}).get('dateTime', 'No time')})")
        
        print("✅ MCP client integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ MCP client integration test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_mcp_integration()) 