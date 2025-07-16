'use client';

import { Event } from '@/types/event';
import { format } from 'date-fns';
import { Calendar, Clock, MapPin, Edit, Trash2 } from 'lucide-react';

interface EventCardProps {
    event: Event;
    onEdit?: (event: Event) => void;
    onDelete?: (eventId: string) => void;
    recentlyCreated?: boolean;
    conflict?: boolean;
    conflictWith?: string[];
}

const priorityColors = {
    low: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-red-100 text-red-800',
};

const statusColors = {
    scheduled: 'bg-blue-100 text-blue-800',
    cancelled: 'bg-gray-100 text-gray-800',
    completed: 'bg-green-100 text-green-800',
};

export default function EventCard({ event, onEdit, onDelete, recentlyCreated, conflict, conflictWith }: EventCardProps) {
    const formatDateTime = (dateString: string) => {
        try {
            const date = new Date(dateString);
            return format(date, 'MMM dd, yyyy h:mm a');
        } catch {
            return dateString;
        }
    };

    return (
        <div
            className={`card hover:shadow-md transition-shadow duration-200 ${recentlyCreated ? 'ring-2 ring-green-400 ring-offset-2' : ''} ${conflict ? 'border-2 border-red-500' : ''}`}
            title={conflict && conflictWith && conflictWith.length ? `Conflicts with: ${conflictWith.join(', ')}` : undefined}
        >
            <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                    {event.title}
                    {conflict && (
                        <span className="ml-1 px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded-full flex items-center gap-1">
                            <svg className="w-3 h-3 text-red-500" fill="currentColor" viewBox="0 0 20 20"><path d="M18 10A8 8 0 11 2 10a8 8 0 0116 0zm-7 4a1 1 0 102 0 1 1 0 00-2 0zm.293-7.707a1 1 0 011.414 0l.007.007a1 1 0 01.293.7v3a1 1 0 11-2 0v-3a1 1 0 01.293-.707z" /></svg>
                            Conflict
                        </span>
                    )}
                </h3>
                <div className="flex gap-2">
                    {onEdit && (
                        <button
                            onClick={() => onEdit(event)}
                            className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                            title="Edit event"
                        >
                            <Edit size={16} />
                        </button>
                    )}
                    {onDelete && (
                        <button
                            onClick={() => onDelete(event.id)}
                            className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                            title="Delete event"
                        >
                            <Trash2 size={16} />
                        </button>
                    )}
                </div>
            </div>

            {event.description && (
                <p className="text-gray-600 mb-4">{event.description}</p>
            )}

            <div className="space-y-2 mb-4">
                <div className="flex items-center text-sm text-gray-600">
                    <Calendar size={16} className="mr-2" />
                    <span>{formatDateTime(event.start_time)}</span>
                </div>

                <div className="flex items-center text-sm text-gray-600">
                    <Clock size={16} className="mr-2" />
                    <span>Duration: {format(new Date(event.end_time), 'h:mm a')}</span>
                </div>

                {event.location && (
                    <div className="flex items-center text-sm text-gray-600">
                        <MapPin size={16} className="mr-2" />
                        <span>{event.location}</span>
                    </div>
                )}
            </div>

            <div className="flex gap-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${priorityColors[event.priority]}`}>
                    {event.priority}
                </span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[event.status]}`}>
                    {event.status}
                </span>
            </div>
        </div>
    );
} 