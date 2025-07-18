'use client';

import { useState, useEffect } from 'react';
import { Calendar, CheckCircle, XCircle, RefreshCw, ExternalLink } from 'lucide-react';

interface StorageStatus {
    primary_storage: 'google_calendar' | 'json';
    google_calendar_available: boolean;
    fallback_available: boolean;
}

export default function GoogleCalendarStatus() {
    const [status, setStatus] = useState<StorageStatus | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isConnecting, setIsConnecting] = useState(false);

    const fetchStatus = async () => {
        try {
            setIsLoading(true);
            const response = await fetch('http://localhost:8000/api/storage/status');
            const data = await response.json();
            setStatus(data);
        } catch (error) {
            console.error('Failed to fetch storage status:', error);
            setStatus({
                primary_storage: 'json',
                google_calendar_available: false,
                fallback_available: true
            });
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchStatus();
    }, []);

    const connectToGoogle = async () => {
        setIsConnecting(true);
        try {
            // Open Google OAuth in a new window
            window.open('http://localhost:8000/api/auth/google', '_blank');

            // Poll for status changes
            const checkStatus = async () => {
                await fetchStatus();
                if (status?.google_calendar_available) {
                    setIsConnecting(false);
                } else {
                    setTimeout(checkStatus, 2000);
                }
            };

            setTimeout(checkStatus, 2000);
        } catch (error) {
            console.error('Failed to connect to Google Calendar:', error);
            setIsConnecting(false);
        }
    };

    if (isLoading) {
        return (
            <div className="card">
                <div className="flex items-center gap-2 mb-4">
                    <Calendar className="h-5 w-5 text-primary-600" />
                    <h3 className="text-lg font-semibold">Calendar Status</h3>
                </div>
                <div className="flex items-center gap-2 text-gray-600">
                    <RefreshCw size={16} className="animate-spin" />
                    <span>Checking connection...</span>
                </div>
            </div>
        );
    }

    return (
        <div className="card">
            <div className="flex items-center gap-2 mb-4">
                <Calendar className="h-5 w-5 text-primary-600" />
                <h3 className="text-lg font-semibold">Calendar Status</h3>
            </div>

            {/* Status Display */}
            <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Primary Storage:</span>
                    <div className="flex items-center gap-2">
                        {status?.primary_storage === 'google_calendar' ? (
                            <>
                                <CheckCircle className="h-4 w-4 text-green-500" />
                                <span className="text-sm text-green-600 font-medium">Google Calendar</span>
                            </>
                        ) : (
                            <>
                                <XCircle className="h-4 w-4 text-gray-400" />
                                <span className="text-sm text-gray-600 font-medium">Local Storage</span>
                            </>
                        )}
                    </div>
                </div>

                <div className="flex items-center gap-4 text-sm text-gray-600">
                    <div className="flex items-center gap-1">
                        {status?.google_calendar_available ? (
                            <CheckCircle className="h-4 w-4 text-green-500" />
                        ) : (
                            <XCircle className="h-4 w-4 text-red-500" />
                        )}
                        <span>Google Calendar: {status?.google_calendar_available ? 'Connected' : 'Disconnected'}</span>
                    </div>
                </div>
            </div>

            {/* Connect Button */}
            {!status?.google_calendar_available && (
                <div className="mb-4">
                    <button
                        onClick={connectToGoogle}
                        disabled={isConnecting}
                        className="btn-primary flex items-center gap-2 w-full disabled:opacity-50"
                    >
                        <ExternalLink size={16} />
                        {isConnecting ? 'Connecting...' : 'Connect to Google Calendar'}
                    </button>
                </div>
            )}

            {/* Info */}
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-800">
                    <strong>Smart Storage:</strong> Events are automatically saved to Google Calendar when connected,
                    with local storage as a fallback. This ensures your events are always accessible.
                </p>
            </div>
        </div>
    );
} 