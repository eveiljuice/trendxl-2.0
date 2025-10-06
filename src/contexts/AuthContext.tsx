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
      if (!mounted) return;
      
      console.log('🔄 Auth state changed:', _event, session ? 'with session' : 'no session');

      // Handle token refresh
      if (_event === 'TOKEN_REFRESHED' && session) {
        console.log('🔄 Token refreshed, updating local storage');
        const newToken = session.access_token;
        setToken(newToken);
        localStorage.setItem('auth_token', newToken);
        // Verify new token to update user data
        await verifyToken(newToken);
        return;
      }

      // Handle sign out
      if (_event === 'SIGNED_OUT') {
        console.log('❌ User signed out');
        setToken(null);
        setUser(null);
        localStorage.removeItem('auth_token');
        setIsLoading(false);
      }

      // Handle token expired - try to refresh
      if (_event === 'TOKEN_EXPIRED') {
        console.log('⚠️ Token expired, attempting refresh...');
        const { data: { session: newSession }, error } = await supabase.auth.refreshSession();
        
        if (error || !newSession) {
          console.error('❌ Failed to refresh token:', error);
          setToken(null);
          setUser(null);
          localStorage.removeItem('auth_token');
          setIsLoading(false);
        } else {
          console.log('✅ Token refreshed successfully');
          const newToken = newSession.access_token;
          setToken(newToken);
          localStorage.setItem('auth_token', newToken);
          await verifyToken(newToken);
        }
      }
    });

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, []);

  // Verify token and load user data
  const verifyToken = async (authToken: string, retryCount = 0): Promise<boolean> => {
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
      return true;
      
    } catch (error: any) {
      console.error('❌ Token verification failed:', error.message);

      // If token is expired (401), try to refresh it once
      if ((error.response?.status === 401 || error.response?.status === 403) && retryCount === 0) {
        console.log('🔄 Token expired, attempting to refresh via Supabase...');
        
        try {
          const { data: { session: newSession }, error: refreshError } = await supabase.auth.refreshSession();
          
          if (refreshError || !newSession) {
            throw new Error('Failed to refresh session');
          }
          
          console.log('✅ Token refreshed successfully, retrying verification');
          const newToken = newSession.access_token;
          setToken(newToken);
          localStorage.setItem('auth_token', newToken);
          
          // Retry verification with new token (but only once)
          return await verifyToken(newToken, 1);
          
        } catch (refreshError) {
          console.error('❌ Failed to refresh token:', refreshError);
          // Clear everything if refresh fails
          localStorage.removeItem('auth_token');
          setToken(null);
          setUser(null);
          await supabase.auth.signOut();
          return false;
        }
      }
      
      // If still unauthorized after refresh or other error
      if (error.response?.status === 401 || error.response?.status === 403) {
        console.log('🗑️ Clearing invalid token');
        localStorage.removeItem('auth_token');
        setToken(null);
        setUser(null);
        await supabase.auth.signOut();
        return false;
      } else {
        // Network error or other issue - keep the token for retry
        console.log('⚠️ Network error, keeping token for retry');
        return false;
      }
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      const response = await axios.post(`${API_URL}/api/v1/auth/login`, {
        email,
        password,
      });

      const { access_token, user: userData } = response.data;
      
      setToken(access_token);
      setUser(userData);
      localStorage.setItem('auth_token', access_token);
      
      // CRITICAL: Set loading to false after successful login
      setIsLoading(false);
      console.log('✅ Login successful, user ID:', userData.id);
    } catch (error: any) {
      setIsLoading(false);
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
      setIsLoading(true);
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
      
      // CRITICAL: Set loading to false after successful registration
      setIsLoading(false);
      console.log('✅ Registration successful, user ID:', userData.id);
    } catch (error: any) {
      setIsLoading(false);
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
