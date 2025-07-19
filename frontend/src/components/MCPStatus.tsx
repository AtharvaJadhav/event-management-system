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

export default function MCPStatus() {
    const [mcpStatus, setMcpStatus] = useState<MCPStatus | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchMcpStatus();
        const interval = setInterval(fetchMcpStatus, 10000); // Refresh every 10 seconds
        return () => clearInterval(interval);
    }, []);

    const fetchMcpStatus = async () => {
        try {
            const response = await fetch('/api/mcp/status');
            if (response.ok) {
                const data = await response.json();
                setMcpStatus(data);
                setError(null);
            } else {
                setError('Failed to fetch MCP status');
            }
        } catch (err) {
            setError('Error connecting to MCP server');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                <div className="flex items-center space-x-3">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                    <span className="text-gray-600">Checking MCP connection...</span>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
                <div className="flex items-center space-x-3">
                    <XCircle className="h-6 w-6 text-red-500" />
                    <div>
                        <h3 className="text-sm font-medium text-red-800">MCP Connection Error</h3>
                        <p className="text-sm text-red-600">{error}</p>
                    </div>
                </div>
            </div>
        );
    }

    if (!mcpStatus) {
        return null;
    }

    const getStatusIcon = () => {
        if (mcpStatus.mcp_connected && mcpStatus.connection_health === 'excellent') {
            return <CheckCircle className="h-6 w-6 text-green-500" />;
        } else if (mcpStatus.mcp_connected) {
            return <AlertTriangle className="h-6 w-6 text-yellow-500" />;
        } else {
            return <XCircle className="h-6 w-6 text-red-500" />;
        }
    };

    const getStatusText = () => {
        if (mcpStatus.mcp_connected && mcpStatus.connection_health === 'excellent') {
            return 'Connected via MCP';
        } else if (mcpStatus.mcp_connected) {
            return 'MCP Connected (Limited)';
        } else {
            return 'MCP Disconnected';
        }
    };

    const getStatusColor = () => {
        if (mcpStatus.mcp_connected && mcpStatus.connection_health === 'excellent') {
            return 'text-green-800 bg-green-50 border-green-200';
        } else if (mcpStatus.mcp_connected) {
            return 'text-yellow-800 bg-yellow-50 border-yellow-200';
        } else {
            return 'text-red-800 bg-red-50 border-red-200';
        }
    };

    return (
        <div className={`border rounded-lg p-6 mb-6 ${getStatusColor()}`}>
            <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                    {getStatusIcon()}
                    <div>
                        <h3 className="text-lg font-semibold">{getStatusText()}</h3>
                        <p className="text-sm opacity-75">
                            Protocol: Model Context Protocol (MCP)
                        </p>
                    </div>
                </div>
                <div className="text-right">
                    <div className="text-sm font-medium">Storage</div>
                    <div className="text-xs opacity-75">
                        Primary: {mcpStatus.primary_storage}
                    </div>
                    <div className="text-xs opacity-75">
                        Fallback: {mcpStatus.fallback_storage}
                    </div>
                </div>
            </div>

            <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                <div>
                    <span className="font-medium">Server Status:</span>
                    <span className={`ml-2 px-2 py-1 rounded text-xs ${mcpStatus.mcp_server_available
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                        }`}>
                        {mcpStatus.mcp_server_available ? 'Available' : 'Unavailable'}
                    </span>
                </div>
                <div>
                    <span className="font-medium">Health:</span>
                    <span className={`ml-2 px-2 py-1 rounded text-xs ${mcpStatus.connection_health === 'excellent'
                        ? 'bg-green-100 text-green-800'
                        : mcpStatus.connection_health === 'good'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                        {mcpStatus.connection_health}
                    </span>
                </div>
            </div>

            {mcpStatus.mcp_connected && (
                <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded">
                    <div className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                        <span className="text-sm text-blue-800">
                            Events are being processed through MCP protocol with Google Calendar integration
                        </span>
                    </div>
                </div>
            )}
        </div>
    );
} 