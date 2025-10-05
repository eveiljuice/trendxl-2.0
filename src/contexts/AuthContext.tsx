import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';
import { supabase } from '../lib/supabase';

// Use the same logic as backendApi.ts
// На Vercel используем относительные пути (фронтенд и API на одном домене)
// В development используем localhost
const API_URL = import.meta.env.VITE_BACKEND_API_URL || 
  (import.meta.env.PROD ? '' : 'http://localhost:8000');

interface User {
  id: string; // UUID from Supabase
  email: string;
  username: string;
  full_name?: string;
  avatar_url?: string;
  bio?: string;
  created_at: string;
  last_login?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  updateProfile: (data: { full_name?: string; avatar_url?: string; bio?: string }) => Promise<void>;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load token and check Supabase session on mount
  useEffect(() => {
    let mounted = true;
    
    const initAuth = async () => {
      try {
        // Check Supabase session first
        const { data: { session }, error } = await supabase.auth.getSession();
        
        if (error) {
          console.error('Error getting session:', error);
        }
        
        if (!mounted) return;
        
        if (session) {
          console.log('✅ Supabase session found, verifying token');
          setToken(session.access_token);
          localStorage.setItem('auth_token', session.access_token);
          await verifyToken(session.access_token);
        } else {
          // Fallback to localStorage token
          const savedToken = localStorage.getItem('auth_token');
          if (savedToken) {
            console.log('✅ Local token found, verifying');
            setToken(savedToken);
            await verifyToken(savedToken);
          } else {
            console.log('ℹ️ No session or token found');
            if (mounted) {
              setIsLoading(false);
            }
          }
        }
      } catch (error) {
        console.error('Auth initialization error:', error);
        if (mounted) {
          setIsLoading(false);
        }
      }
    };

    initAuth();

    // Listen to auth state changes from Supabase
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (_event, session) => {
      // Ignore INITIAL_SESSION and TOKEN_REFRESHED events to avoid noise
      if (_event === 'INITIAL_SESSION' || _event === 'TOKEN_REFRESHED') {
        return;
      }

      console.log('🔄 Auth state changed:', _event);

      if (session && _event === 'SIGNED_IN') {
        console.log('✅ New session detected');
        setToken(session.access_token);
        localStorage.setItem('auth_token', session.access_token);
        await verifyToken(session.access_token);
      } else if (_event === 'SIGNED_OUT') {
        console.log('❌ User signed out');
        setToken(null);
        setUser(null);
        localStorage.removeItem('auth_token');
      }
    });

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, []);

  // Verify token and load user data
  const verifyToken = async (authToken: string) => {
    try {
      console.log('🔍 Verifying token...');
      const response = await axios.get(`${API_URL}/api/v1/auth/me`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
        timeout: 10000, // 10 second timeout
      });

      console.log('✅ Token verified, user:', response.data.email);
      setUser(response.data);

      // Don't try to restore Supabase session from our custom JWT token
      // Supabase manages its own sessions separately
    } catch (error: any) {
      console.error('❌ Token verification failed:', error.message);

      // Only clear token if it's actually invalid (401/403)
      if (error.response?.status === 401 || error.response?.status === 403) {
        console.log('🗑️ Clearing invalid token');
        localStorage.removeItem('auth_token');
        setToken(null);
        setUser(null);
        // Clear Supabase session as well
        await supabase.auth.signOut();
      } else {
        // Network error or other issue - keep the token for retry
        console.log('⚠️ Network error, keeping token for retry');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      const response = await axios.post(`${API_URL}/api/v1/auth/login`, {
        email,
        password,
      });

      const { access_token, user: userData } = response.data;
      
      setToken(access_token);
      setUser(userData);
      localStorage.setItem('auth_token', access_token);
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Login failed';
      throw new Error(errorMessage);
    }
  };

  const register = async (
    email: string,
    username: string,
    password: string,
    fullName?: string
  ) => {
    try {
      const response = await axios.post(`${API_URL}/api/v1/auth/register`, {
        email,
        username,
        password,
        full_name: fullName,
      });

      const { access_token, user: userData } = response.data;
      
      setToken(access_token);
      setUser(userData);
      localStorage.setItem('auth_token', access_token);
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Registration failed';
      throw new Error(errorMessage);
    }
  };

  const logout = async () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('auth_token');
    // Sign out from Supabase to clear session properly
    await supabase.auth.signOut();
  };

  const updateProfile = async (data: {
    full_name?: string;
    avatar_url?: string;
    bio?: string;
  }) => {
    if (!token) {
      throw new Error('Not authenticated');
    }

    try {
      const response = await axios.put(`${API_URL}/api/v1/auth/profile`, data, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setUser(response.data);
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Profile update failed';
      throw new Error(errorMessage);
    }
  };

  const value: AuthContextType = {
    user,
    token,
    login,
    register,
    logout,
    updateProfile,
    isAuthenticated: !!user && !!token,
    isLoading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
