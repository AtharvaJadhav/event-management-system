export interface Event {
  id: string;
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  location?: string;
  priority: 'low' | 'medium' | 'high';
  status: 'scheduled' | 'cancelled' | 'completed';
  created_at: string;
  updated_at: string;
  google_calendar_id?: string;
}

export interface EventCreate {
  title: string;
  description?: string;
  start_time: string;
  end_time: string;
  location?: string;
  priority?: 'low' | 'medium' | 'high';
  status?: 'scheduled' | 'cancelled' | 'completed';
}

export interface EventUpdate {
  title?: string;
  description?: string;
  start_time?: string;
  end_time?: string;
  location?: string;
  priority?: 'low' | 'medium' | 'high';
  status?: 'scheduled' | 'cancelled' | 'completed';
}

export interface EventParseRequest {
  text: string;
}

export interface EventParseResponse {
  events: Event[];
  conflicts: Array<{
    conflicting_event: Event;
    conflict_type: string;
    message: string;
  }>;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  version: string;
} 