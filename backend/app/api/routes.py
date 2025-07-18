from fastapi import APIRouter, HTTPException, status, Request
from typing import List
import fastapi.responses

from ..models import (
    Event, EventCreate, EventUpdate, EventParseRequest, 
    EventParseResponse, HealthResponse
)
from ..services import event_service
from ..google_calendar import google_calendar_service

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse()


@router.get("/events")
async def get_events():
    """Get all events"""
    try:
        events = event_service.get_all_events()
        # Serialize all events
        events_serialized = []
        for event in events:
            event_dict = event.dict()
            event_dict["start_time"] = event_dict["start_time"].isoformat()
            event_dict["end_time"] = event_dict["end_time"].isoformat()
            event_dict["created_at"] = event_dict["created_at"].isoformat()
            event_dict["updated_at"] = event_dict["updated_at"].isoformat()
            events_serialized.append(event_dict)
        return events_serialized
    except Exception as e:
        print(f"ERROR in get_events endpoint: {e}")
        return {"error": str(e)}

@router.get("/storage/status")
async def get_storage_status():
    """Get the current storage status (Google Calendar vs JSON)"""
    try:
        status = event_service.get_storage_status()
        return status
    except Exception as e:
        print(f"ERROR in get_storage_status endpoint: {e}")
        return {"error": str(e)}


@router.get("/events/{event_id}", response_model=Event)
async def get_event(event_id: str):
    """Get event by ID"""
    event = event_service.get_event_by_id(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event


@router.post("/events/conflicts")
async def check_event_conflicts(event: EventCreate):
    """Check for conflicts before creating an event"""
    conflicts = event_service.check_conflicts(event)
    if conflicts:
        return {"conflicts": conflicts, "has_conflict": True}
    return {"conflicts": [], "has_conflict": False}

@router.post("/events", status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate, request: Request):
    """Create a new event, prevent conflicts"""
    try:
        created_event = event_service.create_event(event)
        # Serialize the event for response
        event_dict = created_event.dict()
        event_dict["start_time"] = event_dict["start_time"].isoformat()
        event_dict["end_time"] = event_dict["end_time"].isoformat()
        event_dict["created_at"] = event_dict["created_at"].isoformat()
        event_dict["updated_at"] = event_dict["updated_at"].isoformat()
        return event_dict
    except HTTPException as e:
        if e.status_code == status.HTTP_409_CONFLICT:
            return fastapi.responses.JSONResponse(
                status_code=409,
                content={"error": e.detail["message"], "conflicts": e.detail["conflicts"]}
            )
        raise
    except Exception as e:
        print(f"ERROR in create_event endpoint: {e}")
        return fastapi.responses.JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@router.put("/events/{event_id}", response_model=Event)
async def update_event(event_id: str, event_update: EventUpdate):
    """Update an existing event"""
    event = event_service.update_event(event_id, event_update)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # Check for conflicts after update
    conflicts = event_service.detect_conflicts(event, exclude_event_id=event_id)
    if conflicts:
        # In a real application, you might want to return conflicts as warnings
        pass
    
    return event


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: str):
    """Delete an event"""
    success = event_service.delete_event(event_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )


@router.post("/events/parse")
async def parse_event_text(request: EventParseRequest):
    try:
        events = event_service.parse_event_text(request.text)
        
        # Save events to JSON file
        saved_events = []
        for event in events:
            try:
                # Convert Event to EventCreate and save
                event_create = EventCreate(**event.dict())
                saved_event = event_service.create_event(event_create)
                print(f"DEBUG: Saved event to JSON: {saved_event.title}")
                saved_events.append(saved_event)
            except HTTPException as e:
                if e.status_code == status.HTTP_409_CONFLICT:
                    print(f"DEBUG: Conflict detected for event: {event.title}")
                    # Return conflict info but don't save the event
                    return {
                        "success": False,
                        "error": "Event conflicts with existing events",
                        "conflicts": e.detail["conflicts"],
                        "events": []
                    }
                else:
                    raise
        
        # Convert all saved events to dicts with ISO-formatted datetimes
        events_serialized = [event.dict() for event in saved_events]
        for e in events_serialized:
            e["start_time"] = e["start_time"].isoformat() if hasattr(e["start_time"], "isoformat") else e["start_time"]
            e["end_time"] = e["end_time"].isoformat() if hasattr(e["end_time"], "isoformat") else e["end_time"]
            e["created_at"] = e["created_at"].isoformat() if hasattr(e["created_at"], "isoformat") else e["created_at"]
            e["updated_at"] = e["updated_at"].isoformat() if hasattr(e["updated_at"], "isoformat") else e["updated_at"]
        
        return {
            "success": True,
            "events": events_serialized,
            "conflicts": []
        }
    except Exception as e:
        print(f"ERROR in parse endpoint: {e}")
        return {
            "success": False,
            "error": str(e),
            "events": [],
            "conflicts": []
        }


@router.post("/events/parse-and-create", response_model=List[Event])
async def parse_and_create_events(request: EventParseRequest):
    """Parse event text and create events"""
    events = event_service.parse_event_text(request.text)
    
    created_events = []
    for event in events:
        # Check for conflicts before creating
        conflicts = event_service.detect_conflicts(event)
        if not conflicts:  # Only create if no conflicts
            created_event = event_service.create_event(EventCreate(**event.dict()))
            created_events.append(created_event)
    
    return created_events 

# Google Calendar Integration Endpoints

@router.get("/auth/google")
async def initiate_google_auth():
    """Initiate Google OAuth flow"""
    try:
        success = google_calendar_service.authenticate()
        if success:
            return {"status": "authenticated", "message": "Successfully authenticated with Google Calendar"}
        else:
            return {"status": "failed", "message": "Failed to authenticate with Google Calendar"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )

@router.get("/auth/status")
async def check_auth_status():
    """Check if user is authenticated with Google Calendar"""
    try:
        if google_calendar_service.service:
            return {"status": "authenticated", "message": "User is authenticated"}
        else:
            return {"status": "not_authenticated", "message": "User is not authenticated"}
    except Exception as e:
        return {"status": "error", "message": f"Error checking auth status: {str(e)}"}

@router.get("/calendar/events")
async def get_google_calendar_events():
    """Fetch events from Google Calendar"""
    try:
        events = google_calendar_service.get_events()
        return {
            "status": "success",
            "events": events,
            "count": len(events)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch Google Calendar events: {str(e)}"
        )

@router.post("/calendar/events")
async def create_google_calendar_event(event: EventCreate):
    """Create a new event in Google Calendar"""
    try:
        google_event = google_calendar_service.create_event(event)
        if google_event:
            return {
                "status": "success",
                "message": "Event created in Google Calendar",
                "event": google_event
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create event in Google Calendar"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create Google Calendar event: {str(e)}"
        )

@router.delete("/calendar/events/{event_id}")
async def delete_google_calendar_event(event_id: str):
    """Delete an event from Google Calendar"""
    try:
        success = google_calendar_service.delete_event(event_id)
        if success:
            return {"status": "success", "message": "Event deleted from Google Calendar"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete event from Google Calendar"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete Google Calendar event: {str(e)}"
        )

@router.get("/calendar/sync")
async def sync_google_calendar():
    """Sync events from Google Calendar and detect conflicts with local events"""
    try:
        sync_result = google_calendar_service.sync_events()
        return {
            "status": "success",
            "message": "Google Calendar sync completed",
            "synced_count": sync_result["synced_count"],
            "google_events": sync_result["google_events"],
            "conflicts": sync_result["conflicts"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync with Google Calendar: {str(e)}"
        ) 