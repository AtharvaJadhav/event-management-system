from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum
import uuid


class EventStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    PUBLISHED = "published"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EventPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    start_time: datetime
    end_time: datetime
    location: Optional[str] = Field(None, max_length=200)
    priority: EventPriority = EventPriority.MEDIUM
    status: EventStatus = EventStatus.DRAFT

    @validator('end_time')
    def end_after_start(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('end_time must be after start_time')
        return v


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=200)
    priority: Optional[EventPriority] = None
    status: Optional[EventStatus] = None


class Event(EventBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    google_calendar_id: Optional[str] = Field(None, description="Google Calendar event ID if synced")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @validator('status')
    def validate_status_transition(cls, v, values, **kwargs):
        # Placeholder for state transition validation logic
        # e.g., prevent moving from COMPLETED back to ACTIVE
        return v


class EventParseRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)


class EventParseResponse(BaseModel):
    events: List[Event]
    conflicts: List[dict] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0" 