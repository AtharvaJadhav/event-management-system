'use client';

import { useState, useEffect } from 'react';
import { Play, Square, Activity, Clock, CheckCircle, AlertCircle } from 'lucide-react';

interface StreamStatus {
    running: boolean;
    events_processed: number;
    last_result: {
        text: string;
        result?: any[];
        created?: any[];
        error?: string;
    } | null;
}

export default function StreamProcessor() {
    const [status, setStatus] = useState<StreamStatus>({
        running: false,
        events_processed: 0,
        last_result: null
    });
    const [isLoading, setIsLoading] = useState(false);

    const fetchStatus = async () => {
        try {
            const response = await fetch('http://localhost:8000/api/stream/status');
            const data = await response.json();
            setStatus(data);
        } catch (error) {
            console.error('Failed to fetch stream status:', error);
        }
    };

    useEffect(() => {
        fetchStatus();
        // Poll status every 2 seconds when running
        const interval = setInterval(() => {
            if (status.running) {
                fetchStatus();
            }
        }, 2000);

        return () => clearInterval(interval);
    }, [status.running]);

    const startStream = async () => {
        setIsLoading(true);
        try {
            await fetch('http://localhost:8000/api/stream/start', { method: 'POST' });
            await fetchStatus();
        } catch (error) {
            console.error('Failed to start stream:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const stopStream = async () => {
        setIsLoading(true);
        try {
            await fetch('http://localhost:8000/api/stream/stop', { method: 'POST' });
            await fetchStatus();
        } catch (error) {
            console.error('Failed to stop stream:', error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="card">
            <div className="flex items-center gap-2 mb-4">
                <Activity className="h-5 w-5 text-primary-600" />
                <h3 className="text-lg font-semibold">Stream Processing</h3>
            </div>

            {/* Status Display */}
            <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Status:</span>
                    <div className="flex items-center gap-2">
                        {status.running ? (
                            <>
                                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                                <span className="text-sm text-green-600 font-medium">Running</span>
                            </>
                        ) : (
                            <>
                                <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                                <span className="text-sm text-gray-600 font-medium">Stopped</span>
                            </>
                        )}
                    </div>
                </div>

                <div className="flex items-center gap-4 text-sm text-gray-600">
                    <div className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        <span>Processed: {status.events_processed}</span>
                    </div>
                </div>
            </div>

            {/* Controls */}
            <div className="flex flex-col gap-2 mb-4">
                <button
                    onClick={startStream}
                    disabled={status.running || isLoading}
                    className="btn-primary flex items-center justify-center gap-2 disabled:opacity-50 w-full"
                >
                    <Play size={16} />
                    Start Processing
                </button>
                <button
                    onClick={stopStream}
                    disabled={!status.running || isLoading}
                    className="btn-secondary flex items-center justify-center gap-2 disabled:opacity-50 w-full"
                >
                    <Square size={16} />
                    Stop Processing
                </button>
            </div>

            {/* Last Result */}
            {status.last_result && (
                <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-start gap-2 mb-2">
                        {status.last_result.error ? (
                            <AlertCircle className="h-4 w-4 text-red-500 mt-0.5" />
                        ) : (
                            <CheckCircle className="h-4 w-4 text-green-500 mt-0.5" />
                        )}
                        <span className="text-sm font-medium text-gray-700">Last Processed:</span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">"{status.last_result.text}"</p>
                    {status.last_result.error ? (
                        <p className="text-sm text-red-600">Error: {status.last_result.error}</p>
                    ) : status.last_result.result && status.last_result.result.length > 0 ? (
                        <div className="text-sm text-green-600">
                            ✓ Parsed {status.last_result.result.length} event(s)
                            {status.last_result.created && status.last_result.created.length > 0 && (
                                <span className="ml-2">• Created {status.last_result.created.length} event(s)</span>
                            )}
                        </div>
                    ) : (
                        <div className="text-sm text-yellow-600">
                            ⚠ No events could be parsed
                        </div>
                    )}
                </div>
            )}

            {/* Info */}
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm text-yellow-800">
                    <strong>Demo Mode:</strong> This simulates processing incoming event messages
                    (emails, texts, etc.) with realistic delays. Events are parsed using AI and
                    checked for conflicts.
                </p>
            </div>
        </div>
    );
} 