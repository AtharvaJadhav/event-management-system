'use client';

import { useState, useEffect } from 'react';
import { Event } from '@/types/event';
import { eventApi } from '@/lib/api';
import EventCard from '@/components/EventCard';
import EventParser from '@/components/EventParser';
import { Calendar, Plus, RefreshCw } from 'lucide-react';

export default function HomePage() {
    const [events, setEvents] = useState<Event[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const loadEvents = async () => {
        try {
            setIsLoading(true);
            setError(null);
            const fetchedEvents = await eventApi.getEvents();
            setEvents(fetchedEvents);
        } catch (err) {
            setError('Failed to load events. Please check if the backend is running.');
            console.error('Load events error:', err);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        loadEvents();
    }, []);

    const handleEventCreated = (newEvents: Event[]) => {
        setEvents(prev => [...prev, ...newEvents]);
    };

    const handleEventDeleted = (eventId: string) => {
        setEvents(prev => prev.filter(event => event.id !== eventId));
    };

    const handleEventUpdated = (updatedEvent: Event) => {
        setEvents(prev => prev.map(event =>
            event.id === updatedEvent.id ? updatedEvent : event
        ));
    };

    const handleDeleteEvent = async (eventId: string) => {
        try {
            await eventApi.deleteEvent(eventId);
            handleEventDeleted(eventId);
        } catch (err) {
            setError('Failed to delete event. Please try again.');
            console.error('Delete error:', err);
        }
    };

    return (
        <div className="container mx-auto px-4 py-8">
            {/* Header */}
            <div className="text-center mb-8">
                <div className="flex items-center justify-center gap-3 mb-4">
                    <Calendar className="h-8 w-8 text-primary-600" />
                    <h1 className="text-3xl font-bold text-gray-900">Event Management System</h1>
                </div>
                <p className="text-gray-600 max-w-2xl mx-auto">
                    Parse unstructured event text, detect conflicts, and manage your calendar events with ease.
                </p>
            </div>

            {/* Error Display */}
            {error && (
                <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-red-700">{error}</p>
                    <button
                        onClick={() => setError(null)}
                        className="mt-2 text-red-600 hover:text-red-800 text-sm underline"
                    >
                        Dismiss
                    </button>
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Event Parser Section */}
                <div className="lg:col-span-1">
                    <EventParser onEventsCreated={handleEventCreated} />
                </div>

                {/* Events List Section */}
                <div className="lg:col-span-2">
                    <div className="card">
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-xl font-semibold">Events ({events.length})</h2>
                            <button
                                onClick={loadEvents}
                                disabled={isLoading}
                                className="btn-secondary flex items-center gap-2 disabled:opacity-50"
                            >
                                <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} />
                                Refresh
                            </button>
                        </div>

                        {isLoading ? (
                            <div className="flex items-center justify-center py-12">
                                <div className="flex items-center gap-2 text-gray-600">
                                    <RefreshCw size={20} className="animate-spin" />
                                    <span>Loading events...</span>
                                </div>
                            </div>
                        ) : events.length === 0 ? (
                            <div className="text-center py-12">
                                <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                                <h3 className="text-lg font-medium text-gray-900 mb-2">No events yet</h3>
                                <p className="text-gray-600 mb-4">
                                    Start by parsing some event text or create events manually.
                                </p>
                                <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
                                    <Plus size={16} />
                                    <span>Try: "Team meeting tomorrow at 2pm"</span>
                                </div>
                            </div>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {events.map((event) => (
                                    <EventCard
                                        key={event.id}
                                        event={event}
                                        onDelete={handleDeleteEvent}
                                    />
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="mt-12 text-center text-gray-500 text-sm">
                <p>
                    Event Management System - Built with FastAPI & Next.js
                </p>
                <p className="mt-1">
                    API Documentation available at{' '}
                    <a
                        href="http://localhost:8000/docs"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary-600 hover:text-primary-700 underline"
                    >
                        http://localhost:8000/docs
                    </a>
                </p>
            </div>
        </div>
    );
} 