'use client';

import { useState } from 'react';
import { EventParseResponse } from '@/types/event';
import { eventApi } from '@/lib/api';
import { Loader2, Send } from 'lucide-react';

interface EventParserProps {
    onEventsParsed?: (events: EventParseResponse) => void;
    onEventsCreated?: (events: any[]) => void;
}

export default function EventParser({ onEventsParsed, onEventsCreated }: EventParserProps) {
    const [text, setText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState<EventParseResponse | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleParse = async () => {
        if (!text.trim()) return;

        setIsLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await eventApi.parseEventText(text);
            setResult(response);
            onEventsParsed?.(response);
        } catch (err) {
            setError('Failed to parse event text. Please try again.');
            console.error('Parse error:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleCreateEvents = async () => {
        if (!text.trim() || !result) return;

        setIsLoading(true);
        setError(null);

        try {
            const createdEvents = await eventApi.parseAndCreateEvents(text);
            onEventsCreated?.(createdEvents);
            setText('');
            setResult(null);
        } catch (err) {
            setError('Failed to create events. Please try again.');
            console.error('Create error:', err);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="card">
            <h2 className="text-xl font-semibold mb-4">Parse Event Text</h2>

            <div className="space-y-4">
                <div>
                    <label htmlFor="event-text" className="block text-sm font-medium text-gray-700 mb-2">
                        Enter event description
                    </label>
                    <textarea
                        id="event-text"
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        placeholder="e.g., Chuck's soccer game moved to Thursday at 3:30pm"
                        className="input-field h-24 resize-none"
                        disabled={isLoading}
                    />
                </div>

                <div className="flex gap-2">
                    <button
                        onClick={handleParse}
                        disabled={!text.trim() || isLoading}
                        className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isLoading ? (
                            <Loader2 size={16} className="animate-spin" />
                        ) : (
                            <Send size={16} />
                        )}
                        Parse Events
                    </button>
                </div>

                {error && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                        <p className="text-red-700 text-sm">{error}</p>
                    </div>
                )}

                {result && (
                    <div className="space-y-4">
                        <div className="p-4 bg-blue-50 border border-blue-200 rounded-md">
                            <h3 className="font-medium text-blue-900 mb-2">Parsed Events ({result.events.length})</h3>
                            {result.events.length > 0 ? (
                                <div className="space-y-2">
                                    {result.events.map((event, index) => (
                                        <div key={index} className="p-3 bg-white rounded border">
                                            <p className="font-medium">{event.title}</p>
                                            <p className="text-sm text-gray-600">
                                                {new Date(event.start_time).toLocaleString()}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-blue-700 text-sm">No events could be parsed from the text.</p>
                            )}
                        </div>

                        {result.conflicts.length > 0 && (
                            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-md">
                                <h3 className="font-medium text-yellow-900 mb-2">Conflicts Found ({result.conflicts.length})</h3>
                                <div className="space-y-2">
                                    {result.conflicts.map((conflict, index) => (
                                        <div key={index} className="p-2 bg-white rounded border">
                                            <p className="text-sm text-yellow-800">{conflict.message}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {result.events.length > 0 && (
                            <button
                                onClick={handleCreateEvents}
                                disabled={isLoading}
                                className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                Create All Events
                            </button>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
} 