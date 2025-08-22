import axios from 'axios';
import { tokenStorage } from '../components/AuthProvider';

type AxiosResponse<T = any> = {
  data: T;
  status: number;
  statusText: string;
  headers: any;
  config: any;
  request?: any;
};

const API_BASE_URL = import.meta.env.VITE_API_URL;

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds for agent responses
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = tokenStorage.get();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid, remove it
      tokenStorage.remove();
      // Redirect to login or refresh the page to trigger auth flow
      window.location.reload();
    }
    return Promise.reject(error);
  }
);

// Types
export interface ChatMessage {
  message: string;
  include_sources?: boolean;
}

export interface ChatResponse {
  response: string;
  sources?: Array<{
    content: string;
    metadata: Record<string, any>;
    score?: number;
  }>;
}

export interface SearchRequest {
  query: string;
  k?: number;
  include_scores?: boolean;
}

export interface SearchResponse {
  query: string;
  results: Array<{
    content: string;
    metadata: Record<string, any>;
    score?: number;
  }>;
}

export interface UploadDocumentResponse {
  success: boolean;
  message: string;
  filename: string;
  chunks_processed: number;
  file_size_bytes: number;
}

export interface StoreInfoResponse {
  document_count: number;
  reranker_enabled: boolean;
  reranker_model?: string;
  store_ready: boolean;
}

export interface HealthResponse {
  status: string;
  chatbot_ready: boolean;
  data_pipeline_ready: boolean;
  file_processor_ready: boolean;
}

export interface SupportedFormatsResponse {
  supported_extensions: string[];
  max_file_size_mb: number;
}

// API Functions
export const chatAPI = {
  sendMessage: async (message: ChatMessage): Promise<ChatResponse> => {
    const response: AxiosResponse<ChatResponse> = await api.post('/api/v1/chat', message);
    return response.data;
  },

  search: async (request: SearchRequest): Promise<SearchResponse> => {
    const response: AxiosResponse<SearchResponse> = await api.post('/api/v1/search', request);
    return response.data;
  },

  uploadDocument: async (file: File): Promise<UploadDocumentResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response: AxiosResponse<UploadDocumentResponse> = await api.post(
      '/api/v1/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  getStoreInfo: async (): Promise<StoreInfoResponse> => {
    const response: AxiosResponse<StoreInfoResponse> = await api.get('/api/v1/store-info');
    return response.data;
  },

  clearMemory: async (): Promise<{ message: string }> => {
    const response = await api.delete('/api/v1/clear-memory');
    return response.data;
  },

  getSupportedFormats: async (): Promise<SupportedFormatsResponse> => {
    const response: AxiosResponse<SupportedFormatsResponse> = await api.get('/api/v1/supported-formats');
    return response.data;
  },

  getHealth: async (): Promise<HealthResponse> => {
    const response: AxiosResponse<HealthResponse> = await api.get('/api/v1/health');
    return response.data;
  },
};

export default api;