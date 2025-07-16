'use client';

import { Event } from '@/types/event';
import { format } from 'date-fns';
import { Calendar, Clock, MapPin, Edit, Trash2 } from 'lucide-react';

interface EventCardProps {
    event: Event;
    onEdit?: (event: Event) => void;
    onDelete?: (eventId: string) => void;
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

export default function EventCard({ event, onEdit, onDelete }: EventCardProps) {
    const formatDateTime = (dateString: string) => {
        try {
            const date = new Date(dateString);
            return format(date, 'MMM dd, yyyy h:mm a');
        } catch {
            return dateString;
        }
    };

    return (
        <div className="card hover:shadow-md transition-shadow duration-200">
            <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-semibold text-gray-900">{event.title}</h3>
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