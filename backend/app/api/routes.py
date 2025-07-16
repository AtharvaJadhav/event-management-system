from fastapi import APIRouter, HTTPException, status, Request
from typing import List
import fastapi.responses

from ..models import (
    Event, EventCreate, EventUpdate, EventParseRequest, 
    EventParseResponse, HealthResponse
)
from ..services import event_service

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