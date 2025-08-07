import React, { useState, useEffect } from 'react';
import { Database, Cpu, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { chatAPI } from '../lib/api';
import type { StoreInfoResponse, HealthResponse } from '../lib/api';

export const StatusPanel: React.FC = () => {
  const [storeInfo, setStoreInfo] = useState<StoreInfoResponse | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [storeResponse, healthResponse] = await Promise.all([
        chatAPI.getStoreInfo(),
        chatAPI.getHealth(),
      ]);
      
      setStoreInfo(storeResponse);
      setHealth(healthResponse);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch status');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const clearMemory = async () => {
    try {
      await chatAPI.clearMemory();
      // You could show a success message here
    } catch (err) {
      console.error('Failed to clear memory:', err);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-center">
          <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-2 text-red-600">
          <AlertCircle className="h-5 w-5" />
          <p className="text-sm">{error}</p>
        </div>
        <button
          onClick={fetchStatus}
          className="mt-2 text-sm text-blue-600 hover:text-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 space-y-6">
      {/* System Health */}
      <div>
        <div className="flex items-center space-x-2 mb-4">
          <Cpu className="h-5 w-5 text-gray-600" />
          <h3 className="font-semibold text-gray-900">System Status</h3>
        </div>
        
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">API Status</span>
            <div className="flex items-center space-x-1">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span className="text-sm text-green-600">{health?.status || 'Unknown'}</span>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Chatbot</span>
            <div className="flex items-center space-x-1">
              {health?.chatbot_ready ? (
                <CheckCircle className="h-4 w-4 text-green-500" />
              ) : (
                <AlertCircle className="h-4 w-4 text-red-500" />
              )}
              <span className={`text-sm ${health?.chatbot_ready ? 'text-green-600' : 'text-red-600'}`}>
                {health?.chatbot_ready ? 'Ready' : 'Not Ready'}
              </span>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">File Upload</span>
            <div className="flex items-center space-x-1">
              {health?.file_processor_ready ? (
                <CheckCircle className="h-4 w-4 text-green-500" />
              ) : (
                <AlertCircle className="h-4 w-4 text-red-500" />
              )}
              <span className={`text-sm ${health?.file_processor_ready ? 'text-green-600' : 'text-red-600'}`}>
                {health?.file_processor_ready ? 'Ready' : 'Not Ready'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Knowledge Base */}
      <div>
        <div className="flex items-center space-x-2 mb-4">
          <Database className="h-5 w-5 text-gray-600" />
          <h3 className="font-semibold text-gray-900">Knowledge Base</h3>
        </div>
        
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Documents</span>
            <span className="text-sm font-medium text-gray-900">
              {storeInfo?.document_count || 0}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Store Ready</span>
            <div className="flex items-center space-x-1">
              {storeInfo?.store_ready ? (
                <CheckCircle className="h-4 w-4 text-green-500" />
              ) : (
                <AlertCircle className="h-4 w-4 text-red-500" />
              )}
              <span className={`text-sm ${storeInfo?.store_ready ? 'text-green-600' : 'text-red-600'}`}>
                {storeInfo?.store_ready ? 'Ready' : 'Not Ready'}
              </span>
            </div>
          </div>
          
          {storeInfo?.reranker_enabled && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Reranker</span>
              <span className="text-sm text-green-600">Enabled</span>
            </div>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="pt-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <button
            onClick={fetchStatus}
            className="flex-1 px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
          >
            <RefreshCw className="h-4 w-4 inline mr-1" />
            Refresh
          </button>
          <button
            onClick={clearMemory}
            className="flex-1 px-3 py-2 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors"
          >
            Clear Memory
          </button>
        </div>
      </div>
    </div>
  );
};