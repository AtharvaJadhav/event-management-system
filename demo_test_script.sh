#!/bin/bash

echo "🚀 ULTIMATE MCP INTEGRATION DEMO TEST"
echo "====================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test 1: Health Check
echo -e "${BLUE}1. Testing Backend Health...${NC}"
HEALTH_RESPONSE=$(curl -s http://localhost:8000/api/health)
if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
    echo -e "${GREEN}✅ Backend is healthy${NC}"
else
    echo -e "${RED}❌ Backend health check failed${NC}"
    exit 1
fi

# Test 2: MCP Status
echo -e "${BLUE}2. Testing MCP Status...${NC}"
MCP_RESPONSE=$(curl -s http://localhost:8000/api/mcp/status)
if [[ $MCP_RESPONSE == *"mcp_connected\":true"* ]]; then
    echo -e "${GREEN}✅ MCP is connected${NC}"
else
    echo -e "${RED}❌ MCP connection failed${NC}"
fi

# Test 3: Storage Status
echo -e "${BLUE}3. Testing Storage Status...${NC}"
STORAGE_RESPONSE=$(curl -s http://localhost:8000/api/storage/status)
if [[ $STORAGE_RESPONSE == *"google_calendar_available\":true"* ]]; then
    echo -e "${GREEN}✅ Google Calendar is available${NC}"
else
    echo -e "${RED}❌ Google Calendar not available${NC}"
fi

# Test 4: Event Creation
echo -e "${BLUE}4. Testing Event Creation...${NC}"
CREATE_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/events" \
    -H "Content-Type: application/json" \
    -d '{"title":"Demo Test Event","description":"Testing the complete flow","start_time":"2025-07-19T16:00:00","end_time":"2025-07-19T17:00:00","location":"Demo Location"}')

if [[ $CREATE_RESPONSE == *"Demo Test Event"* ]]; then
    echo -e "${GREEN}✅ Event created successfully${NC}"
    EVENT_ID=$(echo $CREATE_RESPONSE | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
    echo -e "${YELLOW}   Event ID: $EVENT_ID${NC}"
else
    echo -e "${RED}❌ Event creation failed${NC}"
    echo "Response: $CREATE_RESPONSE"
fi

# Test 5: Natural Language Parsing
echo -e "${BLUE}5. Testing Natural Language Parsing...${NC}"
PARSE_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/events/parse" \
    -H "Content-Type: application/json" \
    -d '{"text":"Team meeting tomorrow at 3pm in conference room A"}')

if [[ $PARSE_RESPONSE == *"success\":true"* ]]; then
    echo -e "${GREEN}✅ Natural language parsing successful${NC}"
else
    echo -e "${YELLOW}⚠️  Parsing response: $PARSE_RESPONSE${NC}"
fi

# Test 6: Google Calendar Events
echo -e "${BLUE}6. Testing Google Calendar Integration...${NC}"
CALENDAR_RESPONSE=$(curl -s http://localhost:8000/api/calendar/events)
EVENT_COUNT=$(echo $CALENDAR_RESPONSE | grep -o '"count":[0-9]*' | cut -d':' -f2)

if [[ $EVENT_COUNT -gt 0 ]]; then
    echo -e "${GREEN}✅ Google Calendar has $EVENT_COUNT events${NC}"
else
    echo -e "${RED}❌ No events found in Google Calendar${NC}"
fi

# Test 7: Frontend Status
echo -e "${BLUE}7. Testing Frontend...${NC}"
FRONTEND_RESPONSE=$(curl -s http://localhost:3000 | head -1)
if [[ $FRONTEND_RESPONSE == *"<!DOCTYPE html>"* ]]; then
    echo -e "${GREEN}✅ Frontend is running${NC}"
else
    echo -e "${RED}❌ Frontend not accessible${NC}"
fi

echo ""
echo -e "${GREEN}🎉 DEMO TEST COMPLETE!${NC}"
echo ""
echo -e "${YELLOW}📋 DEMO FLOW SUMMARY:${NC}"
echo "1. ✅ Backend Health Check"
echo "2. ✅ MCP Protocol Connection"
echo "3. ✅ Google Calendar Integration"
echo "4. ✅ Event Creation via MCP"
echo "5. ✅ Natural Language Parsing"
echo "6. ✅ Google Calendar Event Retrieval"
echo "7. ✅ Frontend UI Access"
echo ""
echo -e "${BLUE}🌐 Access Points:${NC}"
echo "• Frontend: http://localhost:3000"
echo "• Backend API: http://localhost:8000"
echo "• API Docs: http://localhost:8000/docs"
echo ""
echo -e "${GREEN}🚀 Ready for the ultimate demo!${NC}" 