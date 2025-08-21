import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Types
export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

// Note: useAuth hook is now exported from AuthProvider component

// Auth API functions
export const authAPI = {
  login: async (credentials: LoginRequest): Promise<TokenResponse> => {
    const response = await axios.post(`${API_BASE_URL}/api/v1/auth/login`, credentials);
    return response.data;
  },

  getCurrentUser: async (token: string): Promise<User> => {
    const response = await axios.get(`${API_BASE_URL}/api/v1/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  },

  logout: async (): Promise<void> => {
    // Just a placeholder - actual logout is handled client-side
    await axios.post(`${API_BASE_URL}/api/v1/auth/logout`);
  },
};

// Token storage utilities
export const tokenStorage = {
  get: (): string | null => {
    return localStorage.getItem('auth_token');
  },

  set: (token: string): void => {
    localStorage.setItem('auth_token', token);
  },

  remove: (): void => {
    localStorage.removeItem('auth_token');
  },
};