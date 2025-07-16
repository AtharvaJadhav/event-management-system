import axios from 'axios';
import { 
  Event, 
  EventCreate, 
  EventUpdate, 
  EventParseRequest, 
  EventParseResponse,
  HealthResponse 
} from '@/types/event';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const eventApi = {
  // Health check
  health: async (): Promise<HealthResponse> => {
    const response = await api.get('/api/health');
    return response.data;
  },

  // Get all events
  getEvents: async (): Promise<Event[]> => {
    const response = await api.get('/api/events');
    return response.data;
  },

  // Get event by ID
  getEvent: async (id: string): Promise<Event> => {
    const response = await api.get(`/api/events/${id}`);
    return response.data;
  },

  // Create event
  createEvent: async (event: EventCreate): Promise<Event> => {
    const response = await api.post('/api/events', event);
    return response.data;
  },

  // Update event
  updateEvent: async (id: string, event: EventUpdate): Promise<Event> => {
    const response = await api.put(`/api/events/${id}`, event);
    return response.data;
  },

  // Delete event
  deleteEvent: async (id: string): Promise<void> => {
    await api.delete(`/api/events/${id}`);
  },

  // Parse event text
  parseEventText: async (text: string): Promise<EventParseResponse> => {
    const response = await api.post('/api/events/parse', { text });
    return response.data;
  },

  // Parse and create events
  parseAndCreateEvents: async (text: string): Promise<Event[]> => {
    const response = await api.post('/api/events/parse-and-create', { text });
    return response.data;
  },
};

export default api; 