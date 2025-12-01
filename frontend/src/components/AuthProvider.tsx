import React, { createContext, useState, useEffect, useContext } from 'react';
import type { ReactNode } from 'react';
import axios from 'axios';

// const API_BASE_URL = import.meta.env.VITE_API_URL;
const API_BASE_URL = ''; // Используем относительные пути

// === ДЕМО РЕЖИМ ===
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE;
const DEMO_CREDENTIALS = {
  username: 'demo',
  password: 'secret'
};

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

export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (credentials: LoginRequest) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

export const AuthContext = createContext<AuthContextType | null>(null);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = tokenStorage.get();
      
      if (storedToken) {
        // Проверяем существующий токен
        try {
          const userData = await authAPI.getCurrentUser(storedToken);
          setToken(storedToken);
          setUser(userData);
        } catch {
          tokenStorage.remove();
        }
      } else if (DEMO_MODE) {
        // ДЕМО: авто-логин
        try {
          console.log('🚀 DEMO MODE: Авто-логин...');
          const tokenResponse = await authAPI.login(DEMO_CREDENTIALS);
          const newToken = tokenResponse.access_token;
          
          tokenStorage.set(newToken);
          setToken(newToken);
          
          const userData = await authAPI.getCurrentUser(newToken);
          setUser(userData);
          console.log('✅ DEMO MODE: Авторизация успешна для', userData.username);
        } catch (error) {
          console.error('❌ DEMO MODE: Ошибка авто-логина:', error);
        }
      }
      
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (credentials: LoginRequest) => {
    try {
      const tokenResponse = await authAPI.login(credentials);
      const newToken = tokenResponse.access_token;
      
      tokenStorage.set(newToken);
      setToken(newToken);
      
      const userData = await authAPI.getCurrentUser(newToken);
      setUser(userData);
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    tokenStorage.remove();
    setToken(null);
    setUser(null);
    authAPI.logout().catch(() => {});
  };

  const value: AuthContextType = {
    user,
    token,
    login,
    logout,
    isAuthenticated: !!token && !!user,
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">
            {DEMO_MODE ? '🚀 Загрузка демо-режима...' : 'Loading...'}
          </p>
        </div>
      </div>
    );
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
