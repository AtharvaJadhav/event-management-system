'use client';

import { useState, useEffect } from 'react';
import { CheckCircle, XCircle, AlertTriangle } from 'lucide-react';

interface MCPStatus {
    mcp_connected: boolean;
    mcp_server_available: boolean;
    primary_storage: string;
    fallback_storage: string;
    connection_health: string;
}

interface StorageStatus {
    primary_storage: 'google_calendar' | 'json';
    google_calendar_available: boolean;
    fallback_available: boolean;
}

export default function StatusIndicator() {
    const [mcpStatus, setMcpStatus] = useState<MCPStatus | null>(null);
    const [storageStatus, setStorageStatus] = useState<StorageStatus | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchStatuses();
        const interval = setInterval(fetchStatuses, 10000); // Refresh every 10 seconds
        return () => clearInterval(interval);
    }, []);

    const fetchStatuses = async () => {
        try {
            // Fetch MCP status
            const mcpResponse = await fetch('/api/mcp/status');
            if (mcpResponse.ok) {
                const mcpData = await mcpResponse.json();
                setMcpStatus(mcpData);
            }

            // Fetch storage status
            const storageResponse = await fetch('http://localhost:8000/api/storage/status');
            if (storageResponse.ok) {
                const storageData = await storageResponse.json();
                setStorageStatus(storageData);
            }
        } catch (err) {
            console.error('Error fetching statuses:', err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center gap-2 text-sm text-gray-600">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <span>Checking...</span>
            </div>
        );
    }

    const isMCPConnected = mcpStatus?.mcp_connected && mcpStatus?.connection_health === 'excellent';
    const isGoogleConnected = storageStatus?.google_calendar_available;

    return (
        <div className="flex items-center gap-4 text-sm">
            {/* MCP Status */}
            <div className="flex items-center gap-2">
                {isMCPConnected ? (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                ) : (
                    <XCircle className="h-4 w-4 text-red-500" />
                )}
                <span className={isMCPConnected ? 'text-green-700' : 'text-red-700'}>
                    MCP
                </span>
            </div>

            {/* Google Calendar Status */}
            <div className="flex items-center gap-2">
                {isGoogleConnected ? (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                ) : (
                    <XCircle className="h-4 w-4 text-red-500" />
                )}
                <span className={isGoogleConnected ? 'text-green-700' : 'text-red-700'}>
                    Google Calendar
                </span>
            </div>
        </div>
    );
} 