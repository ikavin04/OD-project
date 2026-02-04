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
        
        // First, set user from localStorage for immediate UI update
        if (savedUser) {
          try {
            const parsedUser = JSON.parse(savedUser);
            setUser(parsedUser);
          } catch (error) {
            // Silent fail
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
          }
        } catch (error) {
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          delete api.defaults.headers.common['Authorization'];
          setUser(null);
        }
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (credentials) => {
    try {
      const response = await api.post('/auth/login', credentials);
      
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
      
      return { success: true, user: userData };
      
    } catch (error) {
      console.error('[ERROR] Login error:', error);
      console.error('[ERROR] Error response:', error.response?.data);
      
      const message = error.response?.data?.message || 'Login failed. Please check your credentials.';
      throw new Error(message);
    }
  };

  const logout = () => {
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