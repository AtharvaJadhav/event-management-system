'use client';

import { useState, useEffect } from 'react';
import { Event } from '@/types/event';
import { eventApi } from '@/lib/api';
import EventCard from '@/components/EventCard';
import EventParser from '@/components/EventParser';
import StreamProcessor from '@/components/StreamProcessor';
import StatusIndicator from '@/components/StatusIndicator';
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

    // Helper: check if two events overlap
    function timeOverlap(a: Event, b: Event) {
        return (
            new Date(a.start_time) < new Date(b.end_time) &&
            new Date(a.end_time) > new Date(b.start_time)
        );
    }

    // Detect conflicts and build a map of eventId -> [conflicting titles]
    const conflictMap: Record<string, string[]> = {};
    for (let i = 0; i < events.length; i++) {
        for (let j = i + 1; j < events.length; j++) {
            if (timeOverlap(events[i], events[j])) {
                conflictMap[events[i].id] = conflictMap[events[i].id] || [];
                conflictMap[events[j].id] = conflictMap[events[j].id] || [];
                conflictMap[events[i].id].push(events[j].title);
                conflictMap[events[j].id].push(events[i].title);
            }
        }
    }
    const conflictIds = Object.keys(conflictMap);
    const conflictCount = conflictIds.length;
    const successRate = events.length
        ? Math.round(((events.length - conflictCount) / events.length) * 100)
        : 100;

    // Highlight events created in the last 30 seconds
    const now = Date.now();
    const recentlyCreatedIds = events
        .filter(e => now - new Date(e.created_at).getTime() < 30_000)
        .map(e => e.id);

    return (
        <div className="container mx-auto px-4 py-8">
            {/* Header */}
            <div className="text-center mb-8">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center justify-center gap-3 flex-1">
                        <Calendar className="h-8 w-8 text-primary-600" />
                        <h1 className="text-3xl font-bold text-gray-900">Event Management System</h1>
                    </div>
                    <StatusIndicator />
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

            {/* System Stats Section */}
            <div className="mb-6">
                <div className="card bg-gray-50 border border-gray-200">
                    <h3 className="text-lg font-semibold mb-2 text-gray-800">System Stats</h3>
                    <div className="flex flex-wrap gap-6 text-sm text-gray-700">
                        <div><span className="font-bold">Total Events:</span> {events.length}</div>
                        <div><span className="font-bold">Recently Created:</span> {recentlyCreatedIds.length}</div>
                        <div><span className="font-bold">Conflicts Detected:</span> {conflictCount}</div>
                        <div><span className="font-bold">Success Rate:</span> {successRate}%</div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Event Parser Section */}
                <div className="lg:col-span-1">
                    <EventParser onEventsCreated={handleEventCreated} />
                </div>

                {/* Stream Processor Section */}
                <div className="lg:col-span-1">
                    <StreamProcessor />
                </div>

                {/* Events List Section */}
                <div className="lg:col-span-1">
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
                            <div className="space-y-4">
                                {events.map((event) => (
                                    <EventCard
                                        key={event.id}
                                        event={event}
                                        onDelete={handleDeleteEvent}
                                        recentlyCreated={recentlyCreatedIds.includes(event.id)}
                                        conflict={conflictIds.includes(event.id)}
                                        conflictWith={conflictMap[event.id] || []}
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