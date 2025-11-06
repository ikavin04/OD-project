import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../utils/api';
import toast from 'react-hot-toast';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Simple initialization - check for token and verify user
  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('token');
      const savedUser = localStorage.getItem('user');
      
      if (token) {
        console.log('Token found in localStorage, verifying with server...');
        
        // First, set user from localStorage for immediate UI update
        if (savedUser) {
          try {
            const parsedUser = JSON.parse(savedUser);
            setUser(parsedUser);
            console.log('[OK] User loaded from localStorage:', parsedUser);
          } catch (error) {
            console.log('[ERROR] Failed to parse saved user data');
          }
        }
        
        try {
          // Set the token in axios headers before making request
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
          
          // Try to get current user info to verify token is still valid
          const response = await api.get('/auth/me');
          if (response.data.user) {
            setUser(response.data.user);
            // Update localStorage with fresh user data
            localStorage.setItem('user', JSON.stringify(response.data.user));
            console.log('[OK] Token verified, user updated:', response.data.user);
          }
        } catch (error) {
          console.log('[ERROR] Token verification failed, removing token:', error.response?.data || error.message);
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          delete api.defaults.headers.common['Authorization'];
          setUser(null);
        }
      } else {
        console.log('No token found in localStorage');
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (credentials) => {
    try {
      console.log('[INFO] Starting login process with:', credentials);
      
      const response = await api.post('/auth/login', credentials);
      console.log('[OK] Login API response:', response.data);
      
      const { access_token, user: userData } = response.data;

      if (!access_token || !userData) {
        throw new Error('Invalid response from server');
      }

      // Store token and user data in localStorage
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Set user state
      setUser(userData);
      
      console.log('[OK] Login successful, user set and saved:', userData);
      return { success: true, user: userData };
      
    } catch (error) {
      console.error('[ERROR] Login error:', error);
      console.error('[ERROR] Error response:', error.response?.data);
      
      const message = error.response?.data?.message || 'Login failed. Please check your credentials.';
      throw new Error(message);
    }
  };

  const logout = () => {
    console.log('🚪 Logging out user');
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    delete api.defaults.headers.common['Authorization'];
    setUser(null);
  };

  const value = {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user,
    isStudent: user?.role === 'student',
    isFaculty: ['faculty', 'hod', 'admin'].includes(user?.role),
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};